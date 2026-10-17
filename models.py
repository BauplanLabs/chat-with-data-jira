"""
Medallion pipeline: net revenue by customer region (KAN-29).

Silver base models  : lineitem, orders, customer, nation, region
Silver enriched     : customers_with_region  (customer -> nation -> region)
Gold                : net_revenue_by_customer_region

Source tables (tpch_1 namespace, bronze read-only):
  lineitem  – 6,001,215 rows – l_orderkey, l_extendedprice, l_discount
  orders    – 1,500,000 rows – o_orderkey, o_custkey
  customer  –   150,000 rows – c_custkey, c_nationkey
  nation    –        25 rows – n_nationkey, n_regionkey
  region    –         5 rows – r_regionkey, r_name

Revenue metric: net revenue = l_extendedprice * (1 - l_discount)  (pre-tax, TPC-H canonical)
Geography:      customer region via orders -> customer -> nation -> region
"""

import bauplan
from bauplan.standard_expectations import (
    expect_column_accepted_values,
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
)

_REGIONS = ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST']

# ---------------------------------------------------------------------------
# Silver base models – one per source table, no business logic
# ---------------------------------------------------------------------------


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(columns=['l_orderkey', 'l_extendedprice', 'l_discount'])
def lineitem(
    data=bauplan.Model(
        'tpch_1.lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).select(['l_orderkey', 'l_extendedprice', 'l_discount']).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(columns=['o_orderkey', 'o_custkey'])
def orders(
    data=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).select(['o_orderkey', 'o_custkey']).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(columns=['c_custkey', 'c_nationkey'])
def customer(
    data=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).select(['c_custkey', 'c_nationkey']).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(columns=['n_nationkey', 'n_regionkey'])
def nation(
    data=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_regionkey'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).select(['n_nationkey', 'n_regionkey']).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(columns=['r_regionkey', 'r_name'])
def region(
    data=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).select(['r_regionkey', 'r_name']).to_arrow()


# ---------------------------------------------------------------------------
# Silver enriched model – attaches region name to each customer
# ---------------------------------------------------------------------------


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(columns=['c_custkey', 'customer_region'])
def customers_with_region(
    customers=bauplan.Model('customer', columns=['c_custkey', 'c_nationkey']),
    nations=bauplan.Model('nation', columns=['n_nationkey', 'n_regionkey']),
    regions=bauplan.Model('region', columns=['r_regionkey', 'r_name']),
):
    import polars as pl

    c = pl.from_arrow(customers)
    n = pl.from_arrow(nations)
    r = pl.from_arrow(regions)

    return (
        c.join(n, left_on='c_nationkey', right_on='n_nationkey')
        .join(r, left_on='n_regionkey', right_on='r_regionkey')
        .select([
            pl.col('c_custkey'),
            pl.col('r_name').alias('customer_region'),
        ])
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Gold model – net revenue and order volume by customer region
# ---------------------------------------------------------------------------


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(
    columns=['customer_region', 'net_revenue', 'orders'],
    materialization_strategy='REPLACE',
)
def net_revenue_by_customer_region(
    line_items=bauplan.Model('lineitem', columns=['l_orderkey', 'l_extendedprice', 'l_discount']),
    order_data=bauplan.Model('orders', columns=['o_orderkey', 'o_custkey']),
    customer_regions=bauplan.Model('customers_with_region', columns=['c_custkey', 'customer_region']),
):
    import polars as pl

    li = pl.from_arrow(line_items).with_columns(
        (pl.col('l_extendedprice') * (1 - pl.col('l_discount'))).alias('net_revenue')
    )
    o = pl.from_arrow(order_data)
    cr = pl.from_arrow(customer_regions)

    return (
        li.join(o, left_on='l_orderkey', right_on='o_orderkey')
        .join(cr, left_on='o_custkey', right_on='c_custkey')
        .group_by('customer_region')
        .agg([
            pl.col('net_revenue').sum(),
            pl.col('l_orderkey').n_unique().alias('orders'),
        ])
        .sort('net_revenue', descending=True)
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Silver expectations
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_no_nulls(
    data=bauplan.Model('lineitem', columns=['l_orderkey', 'l_extendedprice', 'l_discount']),
):
    assert expect_column_no_nulls(data, 'l_orderkey'), 'l_orderkey has nulls'
    assert expect_column_no_nulls(data, 'l_extendedprice'), 'l_extendedprice has nulls'
    assert expect_column_no_nulls(data, 'l_discount'), 'l_discount has nulls'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_price_positive(
    data=bauplan.Model('lineitem', columns=['l_extendedprice']),
):
    assert expect_column_mean_greater_than(data, 'l_extendedprice', 0.0), 'l_extendedprice mean not positive'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_orders_no_nulls(
    data=bauplan.Model('orders', columns=['o_orderkey', 'o_custkey']),
):
    assert expect_column_no_nulls(data, 'o_orderkey'), 'o_orderkey has nulls'
    assert expect_column_no_nulls(data, 'o_custkey'), 'o_custkey has nulls'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_orders_orderkey_unique(
    data=bauplan.Model('orders', columns=['o_orderkey']),
):
    assert expect_column_all_unique(data, 'o_orderkey'), 'o_orderkey is not unique'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_customer_no_nulls(
    data=bauplan.Model('customer', columns=['c_custkey', 'c_nationkey']),
):
    assert expect_column_no_nulls(data, 'c_custkey'), 'c_custkey has nulls'
    assert expect_column_no_nulls(data, 'c_nationkey'), 'c_nationkey has nulls'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_customer_custkey_unique(
    data=bauplan.Model('customer', columns=['c_custkey']),
):
    assert expect_column_all_unique(data, 'c_custkey'), 'c_custkey is not unique'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_no_nulls(
    data=bauplan.Model('customers_with_region', columns=['c_custkey', 'customer_region']),
):
    assert expect_column_no_nulls(data, 'c_custkey'), 'c_custkey has nulls'
    assert expect_column_no_nulls(data, 'customer_region'), 'customer_region has nulls'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_valid(
    data=bauplan.Model('customers_with_region', columns=['c_custkey', 'customer_region']),
):
    assert expect_column_all_unique(data, 'c_custkey'), 'c_custkey is not unique'
    assert expect_column_accepted_values(data, 'customer_region', _REGIONS), \
        'customer_region contains unexpected values'
    return True


# ---------------------------------------------------------------------------
# Gold expectations
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_no_nulls(
    data=bauplan.Model(
        'net_revenue_by_customer_region',
        columns=['customer_region', 'net_revenue', 'orders'],
    ),
):
    assert expect_column_no_nulls(data, 'customer_region'), 'customer_region has nulls'
    assert expect_column_no_nulls(data, 'net_revenue'), 'net_revenue has nulls'
    assert expect_column_no_nulls(data, 'orders'), 'orders has nulls'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_unique_regions(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    assert expect_column_all_unique(data, 'customer_region'), \
        'customer_region not unique (expected one row per region)'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_positive_revenue(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    assert expect_column_mean_greater_than(data, 'net_revenue', 0.0), 'net_revenue mean not positive'
    return True


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_valid_regions(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    assert expect_column_accepted_values(data, 'customer_region', _REGIONS), \
        'unexpected region values in gold table'
    return True

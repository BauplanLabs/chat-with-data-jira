"""
Medallion pipeline: net revenue by customer region (KAN-23).

Silver base models  : lineitem, orders, customer, nation, region
Silver enriched     : customers_with_region  (customer -> nation -> region)
Gold                : net_revenue_by_customer_region

See src/pipelines/silver/ and src/pipelines/gold/ for layer documentation.
"""

import bauplan
from bauplan.standard_expectations import (
    expect_column_no_nulls,
    expect_column_all_unique,
    expect_column_accepted_values,
    expect_column_mean_greater_than,
)

# ---------------------------------------------------------------------------
# Silver base models – one per source table, no business logic
# ---------------------------------------------------------------------------


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model()
def lineitem(
    data=bauplan.Model(
        'tpch_1.lineitem',
        columns=[
            'l_orderkey', 'l_partkey', 'l_suppkey', 'l_linenumber',
            'l_quantity', 'l_extendedprice', 'l_discount', 'l_tax',
            'l_returnflag', 'l_linestatus', 'l_shipdate', 'l_commitdate',
            'l_receiptdate', 'l_shipinstruct', 'l_shipmode', 'l_comment',
        ],
    ),
):
    import polars as pl
    return pl.from_arrow(data).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model()
def orders(
    data=bauplan.Model(
        'tpch_1.orders',
        columns=[
            'o_orderkey', 'o_custkey', 'o_orderstatus', 'o_totalprice',
            'o_orderdate', 'o_orderpriority', 'o_clerk', 'o_shippriority',
            'o_comment',
        ],
    ),
):
    import polars as pl
    return pl.from_arrow(data).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model()
def customer(
    data=bauplan.Model(
        'tpch_1.customer',
        columns=[
            'c_custkey', 'c_name', 'c_address', 'c_nationkey',
            'c_phone', 'c_acctbal', 'c_mktsegment', 'c_comment',
        ],
    ),
):
    import polars as pl
    return pl.from_arrow(data).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model()
def nation(
    data=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_name', 'n_regionkey', 'n_comment'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model()
def region(
    data=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name', 'r_comment'],
    ),
):
    import polars as pl
    return pl.from_arrow(data).to_arrow()


# ---------------------------------------------------------------------------
# Silver enriched model – customer with nation and region resolved
# Grain: one row per customer (c_custkey)
# ---------------------------------------------------------------------------


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model()
def customers_with_region(
    customer=bauplan.Model(
        'customer',
        columns=['c_custkey', 'c_nationkey', 'c_mktsegment'],
    ),
    nation=bauplan.Model(
        'nation',
        columns=['n_nationkey', 'n_regionkey', 'n_name'],
    ),
    region=bauplan.Model(
        'region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    import polars as pl

    df_customer = pl.from_arrow(customer)
    df_nation = pl.from_arrow(nation)
    df_region = pl.from_arrow(region)

    return (
        df_customer
        .join(df_nation, left_on='c_nationkey', right_on='n_nationkey', how='inner')
        .join(df_region, left_on='n_regionkey', right_on='r_regionkey', how='inner')
        .select([
            pl.col('c_custkey'),
            pl.col('c_mktsegment'),
            pl.col('n_name').alias('customer_nation'),
            pl.col('r_name').alias('customer_region'),
        ])
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Gold model – net revenue by customer region
# Grain: one row per customer region (5 rows)
# Metric: SUM(l_extendedprice * (1 - l_discount))
# ---------------------------------------------------------------------------


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def net_revenue_by_customer_region(
    lineitem=bauplan.Model(
        'lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
    orders=bauplan.Model(
        'orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
    customers_with_region=bauplan.Model(
        'customers_with_region',
        columns=['c_custkey', 'customer_region'],
    ),
):
    import polars as pl

    df_lineitem = pl.from_arrow(lineitem)
    df_orders = pl.from_arrow(orders)
    df_cwr = pl.from_arrow(customers_with_region)

    return (
        df_lineitem
        .join(df_orders, left_on='l_orderkey', right_on='o_orderkey', how='inner')
        .join(df_cwr, left_on='o_custkey', right_on='c_custkey', how='inner')
        .with_columns(
            (pl.col('l_extendedprice') * (1 - pl.col('l_discount'))).alias('line_net_revenue')
        )
        .group_by('customer_region')
        .agg(pl.col('line_net_revenue').sum().alias('net_revenue'))
        .sort('net_revenue', descending=True)
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Silver expectations
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_no_null_orderkey(
    data=bauplan.Model('lineitem', columns=['l_orderkey']),
):
    """Every line item must reference a valid order."""
    return expect_column_no_nulls(data, 'l_orderkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_no_null_extendedprice(
    data=bauplan.Model('lineitem', columns=['l_extendedprice']),
):
    """Extended price must be present on every line item."""
    return expect_column_no_nulls(data, 'l_extendedprice')


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_no_null_discount(
    data=bauplan.Model('lineitem', columns=['l_discount']),
):
    """Discount rate must be present on every line item."""
    return expect_column_no_nulls(data, 'l_discount')


@bauplan.expectation()
@bauplan.python('3.12')
def test_orders_no_null_orderkey(
    data=bauplan.Model('orders', columns=['o_orderkey']),
):
    """Every order must have a primary key."""
    return expect_column_no_nulls(data, 'o_orderkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_orders_no_null_custkey(
    data=bauplan.Model('orders', columns=['o_custkey']),
):
    """Every order must reference a customer."""
    return expect_column_no_nulls(data, 'o_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customer_no_null_custkey(
    data=bauplan.Model('customer', columns=['c_custkey']),
):
    """Customer primary key must never be null."""
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customer_custkey_unique(
    data=bauplan.Model('customer', columns=['c_custkey']),
):
    """Customer keys must be unique."""
    return expect_column_all_unique(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_nation_nationkey_unique(
    data=bauplan.Model('nation', columns=['n_nationkey']),
):
    """Nation keys must be unique (25 distinct nations)."""
    return expect_column_all_unique(data, 'n_nationkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_region_regionkey_unique(
    data=bauplan.Model('region', columns=['r_regionkey']),
):
    """Region keys must be unique (5 distinct regions)."""
    return expect_column_all_unique(data, 'r_regionkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_region_accepted_names(
    data=bauplan.Model('region', columns=['r_name']),
):
    """Region names must be one of the five TPC-H regions."""
    return expect_column_accepted_values(
        data,
        'r_name',
        ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST'],
    )


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_no_null_custkey(
    data=bauplan.Model('customers_with_region', columns=['c_custkey']),
):
    """Every enriched customer record must have a customer key."""
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_custkey_unique(
    data=bauplan.Model('customers_with_region', columns=['c_custkey']),
):
    """Enriched customer table must have one row per customer."""
    return expect_column_all_unique(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_no_null_region(
    data=bauplan.Model('customers_with_region', columns=['customer_region']),
):
    """Every customer must resolve to a region through nation."""
    return expect_column_no_nulls(data, 'customer_region')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_accepted_regions(
    data=bauplan.Model('customers_with_region', columns=['customer_region']),
):
    """Customer region must be one of the five TPC-H regions."""
    return expect_column_accepted_values(
        data,
        'customer_region',
        ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST'],
    )


# ---------------------------------------------------------------------------
# Gold expectations
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_no_null_region(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    """Every output row must have a customer region label."""
    return expect_column_no_nulls(data, 'customer_region')


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_region_unique(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    """Output must have exactly one row per region — no duplicates."""
    return expect_column_all_unique(data, 'customer_region')


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_accepted_regions(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    """Only the five TPC-H regions may appear in the output."""
    return expect_column_accepted_values(
        data,
        'customer_region',
        ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST'],
    )


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_no_null_net_revenue(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    """Net revenue must be populated for every region."""
    return expect_column_no_nulls(data, 'net_revenue')


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_net_revenue_positive(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    """Net revenue per region must be positive (discount < 1 guarantees this)."""
    return expect_column_mean_greater_than(data, 'net_revenue', 0)

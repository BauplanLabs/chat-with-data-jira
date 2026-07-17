import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


# ── Silver: base models ────────────────────────────────────────────────────────

@bauplan.python('3.11', pip={'polars': '1.42.1'})
@bauplan.model()
def orders(
    source=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
):
    import polars as pl
    return (
        pl.from_arrow(source)
        .select([pl.col('o_orderkey'), pl.col('o_custkey')])
        .to_arrow()
    )


@bauplan.python('3.11', pip={'polars': '1.42.1'})
@bauplan.model()
def customer(
    source=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
):
    import polars as pl
    return (
        pl.from_arrow(source)
        .select([pl.col('c_custkey'), pl.col('c_nationkey')])
        .to_arrow()
    )


@bauplan.python('3.11', pip={'polars': '1.42.1'})
@bauplan.model()
def nation(
    source=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_regionkey'],
    ),
):
    import polars as pl
    return (
        pl.from_arrow(source)
        .select([pl.col('n_nationkey'), pl.col('n_regionkey')])
        .to_arrow()
    )


@bauplan.python('3.11', pip={'polars': '1.42.1'})
@bauplan.model()
def region(
    source=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    import polars as pl
    return (
        pl.from_arrow(source)
        .select([pl.col('r_regionkey'), pl.col('r_name')])
        .to_arrow()
    )


# ── Silver: enriched model ─────────────────────────────────────────────────────

@bauplan.python('3.11', pip={'polars': '1.42.1'})
@bauplan.model()
def customers_with_region(
    customers=bauplan.Model('customer', columns=['c_custkey', 'c_nationkey']),
    nations=bauplan.Model('nation', columns=['n_nationkey', 'n_regionkey']),
    regions=bauplan.Model('region', columns=['r_regionkey', 'r_name']),
):
    import polars as pl
    customers_df = pl.from_arrow(customers)
    nations_df = pl.from_arrow(nations)
    regions_df = pl.from_arrow(regions)

    return (
        customers_df
        .join(nations_df, left_on='c_nationkey', right_on='n_nationkey')
        .join(regions_df, left_on='n_regionkey', right_on='r_regionkey')
        .select([
            pl.col('c_custkey'),
            pl.col('r_name').alias('region'),
        ])
        .to_arrow()
    )


# ── Gold ───────────────────────────────────────────────────────────────────────

@bauplan.python('3.11', pip={'polars': '1.42.1'})
@bauplan.model(materialization_strategy='REPLACE')
def orders_by_region(
    orders=bauplan.Model('orders', columns=['o_orderkey', 'o_custkey']),
    customers=bauplan.Model('customers_with_region', columns=['c_custkey', 'region']),
):
    import polars as pl
    orders_df = pl.from_arrow(orders)
    customers_df = pl.from_arrow(customers)

    return (
        orders_df
        .join(customers_df, left_on='o_custkey', right_on='c_custkey')
        .group_by('region')
        .agg(pl.len().alias('order_count'))
        .sort('order_count', descending=True)
        .to_arrow()
    )


# ── Expectations: Silver ───────────────────────────────────────────────────────

@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_no_null_orderkey(
    data=bauplan.Model('orders', columns=['o_orderkey']),
):
    return expect_column_no_nulls(data, 'o_orderkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_no_null_custkey(
    data=bauplan.Model('orders', columns=['o_custkey']),
):
    return expect_column_no_nulls(data, 'o_custkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customer_no_null_custkey(
    data=bauplan.Model('customer', columns=['c_custkey']),
):
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_nation_no_null_nationkey(
    data=bauplan.Model('nation', columns=['n_nationkey']),
):
    return expect_column_no_nulls(data, 'n_nationkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_region_no_null_regionkey(
    data=bauplan.Model('region', columns=['r_regionkey']),
):
    return expect_column_no_nulls(data, 'r_regionkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_region_no_null_name(
    data=bauplan.Model('region', columns=['r_name']),
):
    return expect_column_no_nulls(data, 'r_name')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customers_with_region_no_null_custkey(
    data=bauplan.Model('customers_with_region', columns=['c_custkey']),
):
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customers_with_region_no_null_region(
    data=bauplan.Model('customers_with_region', columns=['region']),
):
    return expect_column_no_nulls(data, 'region')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customers_with_region_unique_custkey(
    data=bauplan.Model('customers_with_region', columns=['c_custkey']),
):
    return expect_column_all_unique(data, 'c_custkey')


# ── Expectations: Gold ─────────────────────────────────────────────────────────

@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_by_region_no_null_region(
    data=bauplan.Model('orders_by_region', columns=['region']),
):
    return expect_column_no_nulls(data, 'region')


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_by_region_no_null_count(
    data=bauplan.Model('orders_by_region', columns=['order_count']),
):
    return expect_column_no_nulls(data, 'order_count')


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_by_region_unique_region(
    data=bauplan.Model('orders_by_region', columns=['region']),
):
    return expect_column_all_unique(data, 'region')

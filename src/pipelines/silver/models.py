import bauplan


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def lineitem(
    bronze=bauplan.Model(
        'tpch_1.lineitem',
        columns=[
            'l_orderkey',
            'l_extendedprice',
            'l_discount',
        ],
    ),
):
    """Silver base for TPC-H lineitem. Grain: one row per line item.

    Keeps only the columns needed for net-revenue calculation.
    Net revenue = l_extendedprice * (1 - l_discount).
    """
    import polars as pl

    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def orders(
    bronze=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
):
    """Silver base for TPC-H orders. Grain: one row per order header."""
    import polars as pl

    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def customer(
    bronze=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
):
    """Silver base for TPC-H customer. Grain: one row per customer."""
    import polars as pl

    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def nation(
    bronze=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_name', 'n_regionkey'],
    ),
):
    """Silver base for TPC-H nation lookup. Grain: one row per nation (25 rows)."""
    import polars as pl

    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def region(
    bronze=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    """Silver base for TPC-H region lookup. Grain: one row per region (5 rows)."""
    import polars as pl

    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def customer_geography(
    customers=bauplan.Model('customer', columns=['c_custkey', 'c_nationkey']),
    nations=bauplan.Model('nation', columns=['n_nationkey', 'n_regionkey']),
    regions=bauplan.Model('region', columns=['r_regionkey', 'r_name']),
):
    """Customer enriched with nation and region for geographic analysis.

    Grain: one row per customer (c_custkey unique).
    Joins silver-to-silver only — never reads bronze.
    Reusable across any gold model that needs customer region attribution.
    """
    import polars as pl

    cust_df = pl.from_arrow(customers)
    nat_df = pl.from_arrow(nations)
    reg_df = pl.from_arrow(regions)

    return (
        cust_df
        .join(nat_df, left_on='c_nationkey', right_on='n_nationkey')
        .join(reg_df, left_on='n_regionkey', right_on='r_regionkey')
        .select([
            pl.col('c_custkey'),
            pl.col('r_name').alias('region_name'),
        ])
        .to_arrow()
    )

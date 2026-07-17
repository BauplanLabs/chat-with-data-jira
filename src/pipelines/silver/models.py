import bauplan


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def lineitem(
    bronze=bauplan.Model(
        'tpch_1.lineitem',
        columns=[
            'l_orderkey', 'l_partkey', 'l_suppkey', 'l_linenumber',
            'l_quantity', 'l_extendedprice', 'l_discount', 'l_tax',
            'l_returnflag', 'l_linestatus', 'l_shipdate', 'l_commitdate',
            'l_receiptdate',
        ],
    ),
):
    import polars as pl
    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def orders(
    bronze=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey', 'o_orderstatus', 'o_totalprice',
                 'o_orderdate', 'o_orderpriority'],
    ),
):
    import polars as pl
    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def customer(
    bronze=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey', 'c_mktsegment', 'c_acctbal'],
    ),
):
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
    import polars as pl
    return pl.from_arrow(bronze).to_arrow()


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def customer_geography(
    customers=bauplan.Model('customer', columns=['c_custkey', 'c_nationkey', 'c_mktsegment']),
    nations=bauplan.Model('nation', columns=['n_nationkey', 'n_name', 'n_regionkey']),
    regions=bauplan.Model('region', columns=['r_regionkey', 'r_name']),
):
    """Customer enriched with nation and region for geographic analysis.

    Grain: one row per customer (c_custkey).
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
            pl.col('c_mktsegment'),
            pl.col('n_name').alias('nation_name'),
            pl.col('r_name').alias('region_name'),
        ])
        .to_arrow()
    )

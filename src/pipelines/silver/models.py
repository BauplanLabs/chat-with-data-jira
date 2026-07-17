import bauplan


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def lineitem(
    src=bauplan.Model(
        'tpch_1.lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(src)
        .select([
            pl.col('l_orderkey').alias('order_key'),
            pl.col('l_extendedprice').alias('extended_price'),
            pl.col('l_discount').alias('discount'),
        ])
        .to_arrow()
    )


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def orders(
    src=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(src)
        .select([
            pl.col('o_orderkey').alias('order_key'),
            pl.col('o_custkey').alias('customer_key'),
        ])
        .to_arrow()
    )


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def customer(
    src=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(src)
        .select([
            pl.col('c_custkey').alias('customer_key'),
            pl.col('c_nationkey').alias('nation_key'),
        ])
        .to_arrow()
    )


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def nation(
    src=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_regionkey'],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(src)
        .select([
            pl.col('n_nationkey').alias('nation_key'),
            pl.col('n_regionkey').alias('region_key'),
        ])
        .to_arrow()
    )


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def region(
    src=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(src)
        .select([
            pl.col('r_regionkey').alias('region_key'),
            pl.col('r_name').alias('region_name'),
        ])
        .to_arrow()
    )


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def customers_with_region(
    cust=bauplan.Model('customer', columns=['customer_key', 'nation_key']),
    nat=bauplan.Model('nation', columns=['nation_key', 'region_key']),
    reg=bauplan.Model('region', columns=['region_key', 'region_name']),
):
    import polars as pl

    return (
        pl.from_arrow(cust)
        .join(pl.from_arrow(nat), on='nation_key', how='inner')
        .join(pl.from_arrow(reg), on='region_key', how='inner')
        .select([
            pl.col('customer_key'),
            pl.col('region_name').alias('customer_region'),
        ])
        .to_arrow()
    )

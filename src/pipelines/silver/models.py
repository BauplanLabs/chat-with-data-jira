import bauplan


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def lineitem(
    lineitem_raw=bauplan.Model(
        'tpch_1.lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
):
    import polars as pl

    return pl.from_arrow(lineitem_raw).to_arrow()


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def orders(
    orders_raw=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
):
    import polars as pl

    return pl.from_arrow(orders_raw).to_arrow()


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def customer(
    customer_raw=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
):
    import polars as pl

    return pl.from_arrow(customer_raw).to_arrow()


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def nation(
    nation_raw=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_regionkey'],
    ),
):
    import polars as pl

    return pl.from_arrow(nation_raw).to_arrow()


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def region(
    region_raw=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    import polars as pl

    return pl.from_arrow(region_raw).to_arrow()


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def customer_with_region(
    customer_data=bauplan.Model('customer'),
    nation_data=bauplan.Model('nation'),
    region_data=bauplan.Model('region'),
):
    """Customer enriched with their geographic region via nation→region hierarchy."""
    import polars as pl

    df_customer = pl.from_arrow(customer_data)
    df_nation = pl.from_arrow(nation_data)
    df_region = pl.from_arrow(region_data)

    return (
        df_customer
        .join(df_nation, left_on='c_nationkey', right_on='n_nationkey')
        .join(df_region, left_on='n_regionkey', right_on='r_regionkey')
        .select(
            pl.col('c_custkey'),
            pl.col('r_name').alias('region_name'),
        )
        .to_arrow()
    )

import bauplan


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

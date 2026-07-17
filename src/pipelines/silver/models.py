import bauplan
import polars as pl


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def lineitem(
    lineitem_raw=bauplan.Model(
        'tpch_1.lineitem',
        columns=['l_orderkey', 'l_linenumber', 'l_extendedprice', 'l_discount'],
    ),
):
    return (
        pl.from_arrow(lineitem_raw)
        .select(['l_orderkey', 'l_linenumber', 'l_extendedprice', 'l_discount'])
        .to_arrow()
    )


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def orders(
    orders_raw=bauplan.Model(
        'tpch_1.orders',
        columns=['o_orderkey', 'o_custkey', 'o_orderstatus', 'o_orderdate'],
    ),
):
    return (
        pl.from_arrow(orders_raw)
        .select(['o_orderkey', 'o_custkey', 'o_orderstatus', 'o_orderdate'])
        .to_arrow()
    )


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def customer(
    customer_raw=bauplan.Model(
        'tpch_1.customer',
        columns=['c_custkey', 'c_nationkey', 'c_name', 'c_mktsegment'],
    ),
):
    return (
        pl.from_arrow(customer_raw)
        .select(['c_custkey', 'c_nationkey', 'c_name', 'c_mktsegment'])
        .to_arrow()
    )


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def nation(
    nation_raw=bauplan.Model(
        'tpch_1.nation',
        columns=['n_nationkey', 'n_name', 'n_regionkey'],
    ),
):
    return (
        pl.from_arrow(nation_raw)
        .select(['n_nationkey', 'n_name', 'n_regionkey'])
        .to_arrow()
    )


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def region(
    region_raw=bauplan.Model(
        'tpch_1.region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    return (
        pl.from_arrow(region_raw)
        .select(['r_regionkey', 'r_name'])
        .to_arrow()
    )


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def nation_region(
    nation_data=bauplan.Model('nation', columns=['n_nationkey', 'n_name', 'n_regionkey']),
    region_data=bauplan.Model('region', columns=['r_regionkey', 'r_name']),
):
    df_nation = pl.from_arrow(nation_data)
    df_region = pl.from_arrow(region_data)
    return (
        df_nation
        .join(df_region, left_on='n_regionkey', right_on='r_regionkey', how='inner')
        .select(['n_nationkey', 'n_name', 'n_regionkey', 'r_name'])
        .to_arrow()
    )

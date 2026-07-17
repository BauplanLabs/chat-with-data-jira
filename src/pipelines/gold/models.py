import bauplan
import polars as pl


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.19.0'})
def net_revenue_by_customer_region(
    lineitem=bauplan.Model(
        'bauplan.lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
    orders=bauplan.Model(
        'bauplan.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
    customer=bauplan.Model(
        'bauplan.customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
    nation_region=bauplan.Model(
        'bauplan.nation_region',
        columns=['n_nationkey', 'r_name'],
    ),
):
    df_lineitem = pl.from_arrow(lineitem)
    df_orders = pl.from_arrow(orders)
    df_customer = pl.from_arrow(customer)
    df_nation_region = pl.from_arrow(nation_region)

    return (
        df_lineitem
        .join(df_orders, left_on='l_orderkey', right_on='o_orderkey', how='inner')
        .join(df_customer, left_on='o_custkey', right_on='c_custkey', how='inner')
        .join(df_nation_region, left_on='c_nationkey', right_on='n_nationkey', how='inner')
        .with_columns(
            (pl.col('l_extendedprice') * (1 - pl.col('l_discount'))).alias('net_revenue_line'),
        )
        .group_by('r_name')
        .agg(
            pl.col('net_revenue_line').sum().alias('net_revenue'),
            pl.col('l_orderkey').n_unique().alias('order_count'),
        )
        .rename({'r_name': 'region'})
        .sort('net_revenue', descending=True)
        .to_arrow()
    )

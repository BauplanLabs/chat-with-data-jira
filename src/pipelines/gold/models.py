import bauplan


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '1.37'})
def revenue_by_customer_region(
    lineitem_data=bauplan.Model(
        'silver.lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
    orders_data=bauplan.Model(
        'silver.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
    customer_region_data=bauplan.Model(
        'silver.customer_with_region',
        columns=['c_custkey', 'region_name'],
    ),
):
    """Net revenue (extended price after discount) aggregated by customer region."""
    import polars as pl

    df_lineitem = pl.from_arrow(lineitem_data)
    df_orders = pl.from_arrow(orders_data)
    df_customer_region = pl.from_arrow(customer_region_data)

    return (
        df_lineitem
        .with_columns(
            (pl.col('l_extendedprice') * (1 - pl.col('l_discount'))).alias('net_revenue')
        )
        .join(df_orders, left_on='l_orderkey', right_on='o_orderkey')
        .join(df_customer_region, left_on='o_custkey', right_on='c_custkey')
        .group_by('region_name')
        .agg(pl.col('net_revenue').sum())
        .select(
            pl.col('region_name').alias('region'),
            pl.col('net_revenue'),
        )
        .sort('net_revenue', descending=True)
        .to_arrow()
    )

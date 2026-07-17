import bauplan


@bauplan.python('3.12', pip={'polars': '1.26.0'})
@bauplan.model(materialization_strategy='REPLACE')
def revenue_by_customer_region(
    lineitems=bauplan.Model(
        'silver.lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
    orders=bauplan.Model(
        'silver.orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
    customer_geo=bauplan.Model(
        'silver.customer_geography',
        columns=['c_custkey', 'region_name'],
    ),
):
    """Net revenue and order count by customer region.

    Grain: one row per region (five regions total).
    Metric: net_revenue = SUM(l_extendedprice * (1 - l_discount)) at the line-item grain.
    order_count: COUNT(DISTINCT order_key) per region.
    """
    import polars as pl

    li = pl.from_arrow(lineitems)
    ord_df = pl.from_arrow(orders)
    cg = pl.from_arrow(customer_geo)

    return (
        li
        .with_columns(
            (pl.col('l_extendedprice') * (1 - pl.col('l_discount'))).alias('net_revenue')
        )
        .join(ord_df, left_on='l_orderkey', right_on='o_orderkey')
        .join(cg, left_on='o_custkey', right_on='c_custkey')
        .group_by('region_name')
        .agg([
            pl.col('net_revenue').sum().alias('net_revenue'),
            pl.col('l_orderkey').n_unique().alias('order_count'),
        ])
        .sort('net_revenue', descending=True)
        .to_arrow()
    )

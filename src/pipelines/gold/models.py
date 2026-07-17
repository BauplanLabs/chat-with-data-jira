import bauplan


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

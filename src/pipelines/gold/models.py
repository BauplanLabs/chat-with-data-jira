import bauplan


@bauplan.python('3.12', pip={'polars': '1.37'})
@bauplan.model(materialization_strategy='REPLACE')
def net_revenue_by_customer_region(
    li=bauplan.Model('lineitem', columns=['order_key', 'extended_price', 'discount']),
    ord=bauplan.Model('orders', columns=['order_key', 'customer_key']),
    cwr=bauplan.Model('customers_with_region', columns=['customer_key', 'customer_region']),
):
    import polars as pl

    return (
        pl.from_arrow(li)
        .join(pl.from_arrow(ord), on='order_key', how='inner')
        .join(pl.from_arrow(cwr), on='customer_key', how='inner')
        .group_by('customer_region')
        .agg(
            (pl.col('extended_price') * (1 - pl.col('discount'))).sum().alias('net_revenue')
        )
        .sort('net_revenue', descending=True)
        .to_arrow()
    )

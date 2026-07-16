import bauplan


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders_by_customer_region(
    orders=bauplan.Model("orders", columns=["o_orderkey", "o_custkey"]),
    customer_with_region=bauplan.Model(
        "customer_with_region", columns=["c_custkey", "customer_region"]
    ),
):
    import polars as pl

    df_orders = pl.from_arrow(orders)
    df_cwr = pl.from_arrow(customer_with_region)

    return (
        df_orders
        .join(df_cwr, left_on="o_custkey", right_on="c_custkey")
        .group_by("customer_region")
        .agg(pl.len().alias("order_count"))
        .sort("order_count", descending=True)
        .to_arrow()
    )

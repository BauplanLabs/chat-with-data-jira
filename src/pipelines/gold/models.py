import bauplan


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders_by_customer_region(
    orders=bauplan.Model("silver.orders", columns=["order_key", "cust_key"]),
    customers=bauplan.Model("silver.customer_with_region", columns=["cust_key", "customer_region"]),
):
    """Order count by customer region (not supplier region)."""
    import polars as pl

    df_o = pl.from_arrow(orders)
    df_c = pl.from_arrow(customers)

    return (
        df_o.join(df_c, on="cust_key", how="left")
        .group_by("customer_region")
        .agg(pl.len().alias("order_count"))
        .sort("order_count", descending=True)
        .to_arrow()
    )

import bauplan


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def revenue_by_customer_region(
    lineitems=bauplan.Model("silver.lineitem", columns=["order_key", "extended_price", "discount"]),
    orders=bauplan.Model("silver.orders", columns=["order_key", "cust_key"]),
    customers=bauplan.Model("silver.customer_with_region", columns=["cust_key", "customer_region"]),
):
    """Net revenue (extended price after discount) aggregated by customer region."""
    import polars as pl

    df_l = pl.from_arrow(lineitems)
    df_o = pl.from_arrow(orders)
    df_c = pl.from_arrow(customers)

    return (
        df_l.join(df_o, on="order_key", how="left")
        .join(df_c, on="cust_key", how="left")
        .with_columns(
            (pl.col("extended_price") * (1 - pl.col("discount"))).alias("net_revenue")
        )
        .group_by("customer_region")
        .agg(pl.col("net_revenue").sum())
        .sort("net_revenue", descending=True)
        .to_arrow()
    )

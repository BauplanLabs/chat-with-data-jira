import bauplan


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders_by_customer_region(
    silver_orders=bauplan.Model(
        "silver.orders",
        columns=["orderkey", "custkey"],
    ),
    silver_customer_with_region=bauplan.Model(
        "silver.customer_with_region",
        columns=["custkey", "customer_region"],
    ),
):
    """
    Gold: order count grouped by the customer's region.
    Grain: one row per customer region (5 rows for TPC-H).
    Metric: order_count = count of distinct order headers per customer region.
    Region is the customer's region, reached via customer -> nation -> region.
    """
    import polars as pl

    orders = pl.DataFrame(silver_orders)
    cust_region = pl.DataFrame(silver_customer_with_region)

    return (
        orders.join(cust_region, on="custkey", how="inner")
        .group_by("customer_region")
        .agg(pl.len().alias("order_count"))
        .sort("order_count", descending=True)
        .to_arrow()
    )

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
    Gold model: order count grouped by the customer's region.
    Grain: one row per region (5 rows total for TPC-H).
    Metric: order_count = count of distinct order headers per customer region.

    Returned table:
    | customer_region | order_count |
    |-----------------|-------------|
    | EUROPE          | 303286      |
    | ASIA            | 301740      |
    | AMERICA         | 299103      |
    | AFRICA          | 298994      |
    | MIDDLE EAST     | 296877      |
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

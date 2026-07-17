import bauplan
from bauplan.standard_expectations import (
    expect_column_accepted_values,
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
)


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def revenue_by_customer_region(
    lineitems=bauplan.Model("lineitem"),
    order_headers=bauplan.Model("orders"),
    geo=bauplan.Model("customers_geo"),
):
    """
    Net revenue and distinct order count by customer region.

    Grain: one row per TPC-H region (five rows total).
    Metric: net revenue = SUM(extended_price * (1 - discount)) per docs/semantics.md.
    Region is the customer region (where the buying business sits).
    """
    import polars as pl

    df_li = pl.from_arrow(lineitems).select("orderkey", "extended_price", "discount")
    df_ord = pl.from_arrow(order_headers).select("orderkey", "customer_key")
    df_geo = pl.from_arrow(geo).select("customer_key", "region_name")

    return (
        df_li.join(df_ord, on="orderkey", how="inner")
        .join(df_geo, on="customer_key", how="inner")
        .group_by("region_name")
        .agg(
            (pl.col("extended_price") * (1 - pl.col("discount")))
            .sum()
            .alias("net_revenue"),
            pl.col("orderkey").n_unique().alias("order_count"),
        )
        .sort("net_revenue", descending=True)
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Expectations
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_name_no_nulls(
    data=bauplan.Model("revenue_by_customer_region", columns=["region_name"]),
):
    """No null region names — every row must be attributable to a region."""
    return expect_column_no_nulls(data, "region_name")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_name_unique(
    data=bauplan.Model("revenue_by_customer_region", columns=["region_name"]),
):
    """One row per region — region name must be unique across the five TPC-H regions."""
    return expect_column_all_unique(data, "region_name")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_name_accepted_values(
    data=bauplan.Model("revenue_by_customer_region", columns=["region_name"]),
):
    """Only the five canonical TPC-H regions are valid."""
    return expect_column_accepted_values(
        data,
        "region_name",
        ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"],
    )


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_no_nulls(
    data=bauplan.Model("revenue_by_customer_region", columns=["net_revenue"]),
):
    """No null net revenue — every region must have a computed revenue figure."""
    return expect_column_no_nulls(data, "net_revenue")


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_positive(
    data=bauplan.Model("revenue_by_customer_region", columns=["net_revenue"]),
):
    """Net revenue must be strictly positive — TPC-H discounts are [0, 0.1], price > 0."""
    return expect_column_mean_greater_than(data, "net_revenue", 0.0)


@bauplan.expectation()
@bauplan.python("3.12")
def test_order_count_no_nulls(
    data=bauplan.Model("revenue_by_customer_region", columns=["order_count"]),
):
    """No null order counts."""
    return expect_column_no_nulls(data, "order_count")

"""
KAN-11: Orders by customer region — medallion pipeline.

Silver base models:  orders, customer, nation, region
Silver enriched:     customer_with_region
Gold:                orders_by_customer_region (materialization_strategy=REPLACE)
"""

import bauplan
from bauplan.standard_expectations import (
    expect_column_no_nulls,
    expect_column_all_unique,
    expect_column_accepted_values,
)

_VALID_REGIONS = ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"]

# ---------------------------------------------------------------------------
# Silver — base models
# ---------------------------------------------------------------------------


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def orders(
    tpch_orders=bauplan.Model("tpch_1.orders"),
):
    import polars as pl

    return pl.from_arrow(tpch_orders).select([
        "o_orderkey",
        "o_custkey",
        "o_orderstatus",
        "o_totalprice",
        "o_orderdate",
        "o_orderpriority",
        "o_clerk",
        "o_shippriority",
        "o_comment",
    ]).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def customer(
    tpch_customer=bauplan.Model("tpch_1.customer"),
):
    import polars as pl

    return pl.from_arrow(tpch_customer).select([
        "c_custkey",
        "c_name",
        "c_address",
        "c_nationkey",
        "c_phone",
        "c_acctbal",
        "c_mktsegment",
        "c_comment",
    ]).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def nation(
    tpch_nation=bauplan.Model("tpch_1.nation"),
):
    import polars as pl

    return pl.from_arrow(tpch_nation).select([
        "n_nationkey",
        "n_name",
        "n_regionkey",
        "n_comment",
    ]).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def region(
    tpch_region=bauplan.Model("tpch_1.region"),
):
    import polars as pl

    return pl.from_arrow(tpch_region).select([
        "r_regionkey",
        "r_name",
        "r_comment",
    ]).to_arrow()


# ---------------------------------------------------------------------------
# Silver — enriched model
# ---------------------------------------------------------------------------


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def customer_with_region(
    customer=bauplan.Model("customer"),
    nation=bauplan.Model("nation"),
    region=bauplan.Model("region"),
):
    """Customer enriched with nation and customer_region via stable reference joins."""
    import polars as pl

    df_customer = pl.from_arrow(customer)
    df_nation = pl.from_arrow(nation)
    df_region = pl.from_arrow(region)

    return (
        df_customer
        .join(df_nation, left_on="c_nationkey", right_on="n_nationkey")
        .join(df_region, left_on="n_regionkey", right_on="r_regionkey")
        .select([
            "c_custkey",
            "c_mktsegment",
            pl.col("n_name").alias("nation_name"),
            pl.col("r_name").alias("customer_region"),
        ])
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Gold
# ---------------------------------------------------------------------------


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders_by_customer_region(
    orders=bauplan.Model("orders", columns=["o_orderkey", "o_custkey"]),
    customer_with_region=bauplan.Model(
        "customer_with_region", columns=["c_custkey", "customer_region"]
    ),
):
    """Count of distinct order headers grouped by the customer's region."""
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


# ---------------------------------------------------------------------------
# Expectations — silver orders
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_no_null_orderkey(
    data=bauplan.Model("orders", columns=["o_orderkey"]),
):
    """No null order keys — every order header must be identified."""
    return expect_column_no_nulls(data, "o_orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_no_null_custkey(
    data=bauplan.Model("orders", columns=["o_custkey"]),
):
    """No null customer keys — every order must link to a customer."""
    return expect_column_no_nulls(data, "o_custkey")


# ---------------------------------------------------------------------------
# Expectations — silver customer
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_no_null_custkey(
    data=bauplan.Model("customer", columns=["c_custkey"]),
):
    """No null customer keys — every customer must have a primary key."""
    return expect_column_no_nulls(data, "c_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_no_null_nationkey(
    data=bauplan.Model("customer", columns=["c_nationkey"]),
):
    """No null nation keys — every customer must belong to a nation."""
    return expect_column_no_nulls(data, "c_nationkey")


# ---------------------------------------------------------------------------
# Expectations — silver nation
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_no_null_nationkey(
    data=bauplan.Model("nation", columns=["n_nationkey"]),
):
    """No null nation keys — every nation must have a primary key."""
    return expect_column_no_nulls(data, "n_nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_no_null_regionkey(
    data=bauplan.Model("nation", columns=["n_regionkey"]),
):
    """No null region keys — every nation must belong to a region."""
    return expect_column_no_nulls(data, "n_regionkey")


# ---------------------------------------------------------------------------
# Expectations — silver region
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_no_null_regionkey(
    data=bauplan.Model("region", columns=["r_regionkey"]),
):
    """No null region keys — every region must have a primary key."""
    return expect_column_no_nulls(data, "r_regionkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_no_null_name(
    data=bauplan.Model("region", columns=["r_name"]),
):
    """No null region names — every region must have a name."""
    return expect_column_no_nulls(data, "r_name")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_unique_keys(
    data=bauplan.Model("region", columns=["r_regionkey"]),
):
    """Region keys are unique — the region dimension has no duplicates."""
    return expect_column_all_unique(data, "r_regionkey")


# ---------------------------------------------------------------------------
# Expectations — silver customer_with_region
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_no_null_custkey(
    data=bauplan.Model("customer_with_region", columns=["c_custkey"]),
):
    """No null customer keys after enrichment — join preserved all customers."""
    return expect_column_no_nulls(data, "c_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_no_null_region(
    data=bauplan.Model("customer_with_region", columns=["customer_region"]),
):
    """No null customer regions — every customer resolved to a region."""
    return expect_column_no_nulls(data, "customer_region")


# ---------------------------------------------------------------------------
# Expectations — gold orders_by_customer_region
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_no_null_region(
    data=bauplan.Model("orders_by_customer_region", columns=["customer_region"]),
):
    """No null customer regions in the gold output."""
    return expect_column_no_nulls(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_no_null_count(
    data=bauplan.Model("orders_by_customer_region", columns=["order_count"]),
):
    """No null order counts — every region produced at least one order."""
    return expect_column_no_nulls(data, "order_count")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_unique_regions(
    data=bauplan.Model("orders_by_customer_region", columns=["customer_region"]),
):
    """Each region appears exactly once — one row per region in the output."""
    return expect_column_all_unique(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_accepted_regions(
    data=bauplan.Model("orders_by_customer_region", columns=["customer_region"]),
):
    """Only the five TPC-H regions appear — no unexpected values from a bad join."""
    return expect_column_accepted_values(data, "customer_region", _VALID_REGIONS)

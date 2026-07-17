import bauplan
from bauplan.standard_expectations import (
    expect_column_accepted_values,
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
)


# ---------------------------------------------------------------------------
# Silver base models
# ---------------------------------------------------------------------------


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def lineitem(
    source=bauplan.Model("tpch_1.lineitem"),
):
    import polars as pl

    return (
        pl.from_arrow(source)
        .select(
            pl.col("l_orderkey").alias("orderkey"),
            pl.col("l_partkey").alias("part_key"),
            pl.col("l_suppkey").alias("supplier_key"),
            pl.col("l_linenumber").alias("line_number"),
            pl.col("l_quantity").alias("quantity"),
            pl.col("l_extendedprice").alias("extended_price"),
            pl.col("l_discount").alias("discount"),
            pl.col("l_tax").alias("tax"),
            pl.col("l_returnflag").alias("return_flag"),
            pl.col("l_linestatus").alias("line_status"),
            pl.col("l_shipdate").alias("ship_date"),
            pl.col("l_commitdate").alias("commit_date"),
            pl.col("l_receiptdate").alias("receipt_date"),
            pl.col("l_shipinstruct").alias("ship_instruct"),
            pl.col("l_shipmode").alias("ship_mode"),
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders(
    source=bauplan.Model("tpch_1.orders"),
):
    import polars as pl

    return (
        pl.from_arrow(source)
        .select(
            pl.col("o_orderkey").alias("orderkey"),
            pl.col("o_custkey").alias("customer_key"),
            pl.col("o_orderstatus").alias("order_status"),
            pl.col("o_totalprice").alias("total_price"),
            pl.col("o_orderdate").alias("order_date"),
            pl.col("o_orderpriority").alias("order_priority"),
            pl.col("o_clerk").alias("clerk"),
            pl.col("o_shippriority").alias("ship_priority"),
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def customer(
    source=bauplan.Model("tpch_1.customer"),
):
    import polars as pl

    return (
        pl.from_arrow(source)
        .select(
            pl.col("c_custkey").alias("customer_key"),
            pl.col("c_name").alias("customer_name"),
            pl.col("c_nationkey").alias("nation_key"),
            pl.col("c_phone").alias("phone"),
            pl.col("c_acctbal").alias("account_balance"),
            pl.col("c_mktsegment").alias("market_segment"),
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def nation(
    source=bauplan.Model("tpch_1.nation"),
):
    import polars as pl

    return (
        pl.from_arrow(source)
        .select(
            pl.col("n_nationkey").alias("nation_key"),
            pl.col("n_name").alias("nation_name"),
            pl.col("n_regionkey").alias("region_key"),
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def region(
    source=bauplan.Model("tpch_1.region"),
):
    import polars as pl

    return (
        pl.from_arrow(source)
        .select(
            pl.col("r_regionkey").alias("region_key"),
            pl.col("r_name").alias("region_name"),
        )
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Silver enriched model
# ---------------------------------------------------------------------------


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def customers_geo(
    customers=bauplan.Model("customer"),
    nations=bauplan.Model("nation"),
    regions=bauplan.Model("region"),
):
    """Customer enriched with nation and region — stable geography lookup."""
    import polars as pl

    df_c = pl.from_arrow(customers)
    df_n = pl.from_arrow(nations)
    df_r = pl.from_arrow(regions)

    return (
        df_c.join(df_n, on="nation_key", how="inner")
        .join(df_r, on="region_key", how="inner")
        .select(
            pl.col("customer_key"),
            pl.col("market_segment"),
            pl.col("nation_name"),
            pl.col("region_name"),
        )
        .to_arrow()
    )


# ---------------------------------------------------------------------------
# Gold model
# ---------------------------------------------------------------------------


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
# Silver expectations
# ---------------------------------------------------------------------------


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_orderkey_no_nulls(
    data=bauplan.Model("lineitem", columns=["orderkey"]),
):
    """No null order keys on lineitem — every line item must belong to an order."""
    return expect_column_no_nulls(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_extended_price_no_nulls(
    data=bauplan.Model("lineitem", columns=["extended_price"]),
):
    """No null extended prices — required for net revenue computation."""
    return expect_column_no_nulls(data, "extended_price")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_discount_no_nulls(
    data=bauplan.Model("lineitem", columns=["discount"]),
):
    """No null discounts — required for net revenue computation."""
    return expect_column_no_nulls(data, "discount")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_no_nulls(
    data=bauplan.Model("orders", columns=["orderkey"]),
):
    """No null order keys on the orders table."""
    return expect_column_no_nulls(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_unique(
    data=bauplan.Model("orders", columns=["orderkey"]),
):
    """Order key is the primary key — must be unique."""
    return expect_column_all_unique(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_customer_key_no_nulls(
    data=bauplan.Model("orders", columns=["customer_key"]),
):
    """Every order must reference a customer."""
    return expect_column_no_nulls(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_key_no_nulls(
    data=bauplan.Model("customer", columns=["customer_key"]),
):
    """No null customer keys."""
    return expect_column_no_nulls(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_key_unique(
    data=bauplan.Model("customer", columns=["customer_key"]),
):
    """Customer key is the primary key — must be unique."""
    return expect_column_all_unique(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_nation_key_no_nulls(
    data=bauplan.Model("customer", columns=["nation_key"]),
):
    """Every customer must belong to a nation."""
    return expect_column_no_nulls(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_key_no_nulls(
    data=bauplan.Model("nation", columns=["nation_key"]),
):
    """No null nation keys."""
    return expect_column_no_nulls(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_key_unique(
    data=bauplan.Model("nation", columns=["nation_key"]),
):
    """Nation key is the primary key — must be unique."""
    return expect_column_all_unique(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_key_no_nulls(
    data=bauplan.Model("region", columns=["region_key"]),
):
    """No null region keys."""
    return expect_column_no_nulls(data, "region_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_key_unique(
    data=bauplan.Model("region", columns=["region_key"]),
):
    """Region key is the primary key — must be unique."""
    return expect_column_all_unique(data, "region_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customers_geo_customer_key_no_nulls(
    data=bauplan.Model("customers_geo", columns=["customer_key"]),
):
    """No null customer keys in the geography lookup."""
    return expect_column_no_nulls(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customers_geo_customer_key_unique(
    data=bauplan.Model("customers_geo", columns=["customer_key"]),
):
    """Geography lookup is one-row-per-customer — customer key must be unique."""
    return expect_column_all_unique(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customers_geo_region_name_no_nulls(
    data=bauplan.Model("customers_geo", columns=["region_name"]),
):
    """Every customer must map to a region — no null region names."""
    return expect_column_no_nulls(data, "region_name")


# ---------------------------------------------------------------------------
# Gold expectations
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

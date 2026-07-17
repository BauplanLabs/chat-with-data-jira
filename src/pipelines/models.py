import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
    expect_column_accepted_values,
)

# =============================================================================
# Silver base models
# =============================================================================


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def lineitem(
    tpch_lineitem=bauplan.Model(
        "tpch_1.lineitem",
        columns=[
            "l_orderkey",
            "l_partkey",
            "l_suppkey",
            "l_linenumber",
            "l_quantity",
            "l_extendedprice",
            "l_discount",
            "l_tax",
            "l_returnflag",
            "l_linestatus",
            "l_shipdate",
            "l_commitdate",
            "l_receiptdate",
        ],
    ),
):
    """Silver base for TPC-H lineitem. Grain: one row per line item."""
    import polars as pl

    return pl.from_arrow(tpch_lineitem).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def orders(
    tpch_orders=bauplan.Model(
        "tpch_1.orders",
        columns=[
            "o_orderkey",
            "o_custkey",
            "o_orderstatus",
            "o_totalprice",
            "o_orderdate",
            "o_orderpriority",
            "o_clerk",
            "o_shippriority",
        ],
    ),
):
    """Silver base for TPC-H orders. Grain: one row per order header."""
    import polars as pl

    return pl.from_arrow(tpch_orders).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def customer(
    tpch_customer=bauplan.Model(
        "tpch_1.customer",
        columns=[
            "c_custkey",
            "c_name",
            "c_nationkey",
            "c_acctbal",
            "c_mktsegment",
        ],
    ),
):
    """Silver base for TPC-H customer. Grain: one row per customer."""
    import polars as pl

    return pl.from_arrow(tpch_customer).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def nation(
    tpch_nation=bauplan.Model(
        "tpch_1.nation",
        columns=["n_nationkey", "n_name", "n_regionkey"],
    ),
):
    """Silver base for TPC-H nation. Grain: one row per nation (25 rows)."""
    import polars as pl

    return pl.from_arrow(tpch_nation).to_arrow()


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def region(
    tpch_region=bauplan.Model(
        "tpch_1.region",
        columns=["r_regionkey", "r_name"],
    ),
):
    """Silver base for TPC-H region. Grain: one row per region (five rows)."""
    import polars as pl

    return pl.from_arrow(tpch_region).to_arrow()


# =============================================================================
# Silver enriched models
# =============================================================================


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def customer_with_region(
    customer=bauplan.Model(
        "customer",
        columns=["c_custkey", "c_nationkey"],
    ),
    nation=bauplan.Model(
        "nation",
        columns=["n_nationkey", "n_regionkey"],
    ),
    region=bauplan.Model(
        "region",
        columns=["r_regionkey", "r_name"],
    ),
):
    """
    Silver enriched: customer with customer region attached.
    Grain: one row per customer (no fanout).
    Joins customer -> nation -> region to resolve the customer region name.
    Uses customer region (buying side); see docs/semantics.md for the
    customer-region vs supplier-region ambiguity.
    """
    import polars as pl

    df_customer = pl.from_arrow(customer)
    df_nation = pl.from_arrow(nation)
    df_region = pl.from_arrow(region)

    return (
        df_customer.join(df_nation, left_on="c_nationkey", right_on="n_nationkey")
        .join(df_region, left_on="n_regionkey", right_on="r_regionkey")
        .select(
            pl.col("c_custkey"),
            pl.col("r_name").alias("customer_region"),
        )
        .to_arrow()
    )


# =============================================================================
# Gold models
# =============================================================================


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def net_revenue_by_customer_region(
    lineitem=bauplan.Model(
        "lineitem",
        columns=["l_orderkey", "l_extendedprice", "l_discount"],
    ),
    orders=bauplan.Model(
        "orders",
        columns=["o_orderkey", "o_custkey"],
    ),
    customer_with_region=bauplan.Model(
        "customer_with_region",
        columns=["c_custkey", "customer_region"],
    ),
):
    """
    Gold: net revenue aggregated by customer region.
    Grain: one row per TPC-H region (five rows).
    Metric: net_revenue = SUM(l_extendedprice * (1 - l_discount)) at line-item grain.
    Sorted descending by net_revenue.

    Interprets "revenue by region" as customer region (buying side).
    See docs/semantics.md for the customer-region vs supplier-region ambiguity.
    Net revenue is pre-tax; see semantics.md for the distinction between
    net revenue and the after-tax order total.
    """
    import polars as pl

    df_lineitem = pl.from_arrow(lineitem)
    df_orders = pl.from_arrow(orders)
    df_cwr = pl.from_arrow(customer_with_region)

    return (
        df_lineitem.join(df_orders, left_on="l_orderkey", right_on="o_orderkey")
        .join(df_cwr, left_on="o_custkey", right_on="c_custkey")
        .with_columns(
            (pl.col("l_extendedprice") * (1 - pl.col("l_discount"))).alias(
                "net_revenue_line"
            )
        )
        .group_by("customer_region")
        .agg(pl.col("net_revenue_line").sum().alias("net_revenue"))
        .sort("net_revenue", descending=True)
        .to_arrow()
    )


# =============================================================================
# Expectations - silver base
# =============================================================================


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_orderkey_no_nulls(
    data=bauplan.Model("lineitem", columns=["l_orderkey"]),
):
    """No null order keys in lineitem."""
    return expect_column_no_nulls(data, "l_orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_extendedprice_no_nulls(
    data=bauplan.Model("lineitem", columns=["l_extendedprice"]),
):
    """No null extended prices in lineitem."""
    return expect_column_no_nulls(data, "l_extendedprice")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_extendedprice_positive(
    data=bauplan.Model("lineitem", columns=["l_extendedprice"]),
):
    """Mean extended price is positive."""
    return expect_column_mean_greater_than(data, "l_extendedprice", 0)


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_discount_no_nulls(
    data=bauplan.Model("lineitem", columns=["l_discount"]),
):
    """No null discount values in lineitem."""
    return expect_column_no_nulls(data, "l_discount")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_no_nulls(
    data=bauplan.Model("orders", columns=["o_orderkey"]),
):
    """No null order keys in orders."""
    return expect_column_no_nulls(data, "o_orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_unique(
    data=bauplan.Model("orders", columns=["o_orderkey"]),
):
    """Order keys are unique (one row per order header)."""
    return expect_column_all_unique(data, "o_orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_custkey_no_nulls(
    data=bauplan.Model("orders", columns=["o_custkey"]),
):
    """No null customer keys in orders."""
    return expect_column_no_nulls(data, "o_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_custkey_no_nulls(
    data=bauplan.Model("customer", columns=["c_custkey"]),
):
    """No null customer keys in customer."""
    return expect_column_no_nulls(data, "c_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_custkey_unique(
    data=bauplan.Model("customer", columns=["c_custkey"]),
):
    """Customer keys are unique."""
    return expect_column_all_unique(data, "c_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_nationkey_no_nulls(
    data=bauplan.Model("customer", columns=["c_nationkey"]),
):
    """No null nation keys in customer."""
    return expect_column_no_nulls(data, "c_nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_nationkey_no_nulls(
    data=bauplan.Model("nation", columns=["n_nationkey"]),
):
    """No null nation keys."""
    return expect_column_no_nulls(data, "n_nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_nationkey_unique(
    data=bauplan.Model("nation", columns=["n_nationkey"]),
):
    """Nation keys are unique (25 nations)."""
    return expect_column_all_unique(data, "n_nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_regionkey_no_nulls(
    data=bauplan.Model("region", columns=["r_regionkey"]),
):
    """No null region keys."""
    return expect_column_no_nulls(data, "r_regionkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_regionkey_unique(
    data=bauplan.Model("region", columns=["r_regionkey"]),
):
    """Region keys are unique (five regions)."""
    return expect_column_all_unique(data, "r_regionkey")


# =============================================================================
# Expectations - silver enriched
# =============================================================================


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_custkey_no_nulls(
    data=bauplan.Model("customer_with_region", columns=["c_custkey"]),
):
    """No null customer keys in enriched customer model."""
    return expect_column_no_nulls(data, "c_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_custkey_unique(
    data=bauplan.Model("customer_with_region", columns=["c_custkey"]),
):
    """Customer keys remain unique after region join (no fanout)."""
    return expect_column_all_unique(data, "c_custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_region_no_nulls(
    data=bauplan.Model("customer_with_region", columns=["customer_region"]),
):
    """Every customer resolved to a region name."""
    return expect_column_no_nulls(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_accepted_values(
    data=bauplan.Model("customer_with_region", columns=["customer_region"]),
):
    """Region names are the five canonical TPC-H regions."""
    return expect_column_accepted_values(
        data,
        "customer_region",
        ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"],
    )


# =============================================================================
# Expectations - gold
# =============================================================================


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_region_no_nulls(
    data=bauplan.Model(
        "net_revenue_by_customer_region", columns=["customer_region"]
    ),
):
    """Every row has a region name."""
    return expect_column_no_nulls(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_region_unique(
    data=bauplan.Model(
        "net_revenue_by_customer_region", columns=["customer_region"]
    ),
):
    """One row per region (five-row table)."""
    return expect_column_all_unique(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_region_accepted_values(
    data=bauplan.Model(
        "net_revenue_by_customer_region", columns=["customer_region"]
    ),
):
    """Region names are the five canonical TPC-H regions."""
    return expect_column_accepted_values(
        data,
        "customer_region",
        ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"],
    )


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_no_nulls(
    data=bauplan.Model(
        "net_revenue_by_customer_region", columns=["net_revenue"]
    ),
):
    """Net revenue is present for all regions."""
    return expect_column_no_nulls(data, "net_revenue")


@bauplan.expectation()
@bauplan.python("3.12")
def test_net_revenue_positive(
    data=bauplan.Model(
        "net_revenue_by_customer_region", columns=["net_revenue"]
    ),
):
    """Net revenue mean is positive (discounts never exceed 100%)."""
    return expect_column_mean_greater_than(data, "net_revenue", 0)

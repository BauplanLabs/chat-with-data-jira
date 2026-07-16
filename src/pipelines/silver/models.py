import bauplan


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders(
    raw=bauplan.Model(
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
    import polars as pl

    return (
        pl.from_arrow(raw)
        .rename(
            {
                "o_orderkey": "order_key",
                "o_custkey": "cust_key",
                "o_orderstatus": "order_status",
                "o_totalprice": "total_price",
                "o_orderdate": "order_date",
                "o_orderpriority": "order_priority",
                "o_clerk": "clerk",
                "o_shippriority": "ship_priority",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def customer(
    raw=bauplan.Model(
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
    import polars as pl

    return (
        pl.from_arrow(raw)
        .rename(
            {
                "c_custkey": "cust_key",
                "c_name": "cust_name",
                "c_nationkey": "nation_key",
                "c_acctbal": "acct_bal",
                "c_mktsegment": "mkt_segment",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def nation(
    raw=bauplan.Model(
        "tpch_1.nation",
        columns=["n_nationkey", "n_name", "n_regionkey"],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(raw)
        .rename(
            {
                "n_nationkey": "nation_key",
                "n_name": "nation_name",
                "n_regionkey": "region_key",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def region(
    raw=bauplan.Model(
        "tpch_1.region",
        columns=["r_regionkey", "r_name"],
    ),
):
    import polars as pl

    return (
        pl.from_arrow(raw)
        .rename(
            {
                "r_regionkey": "region_key",
                "r_name": "region_name",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def customer_with_region(
    customers=bauplan.Model("customer", columns=["cust_key", "cust_name", "nation_key", "acct_bal", "mkt_segment"]),
    nations=bauplan.Model("nation", columns=["nation_key", "nation_name", "region_key"]),
    regions=bauplan.Model("region", columns=["region_key", "region_name"]),
):
    """Customer enriched with its nation and customer region (not supplier region)."""
    import polars as pl

    df_c = pl.from_arrow(customers)
    df_n = pl.from_arrow(nations)
    df_r = pl.from_arrow(regions)

    return (
        df_c.join(df_n, on="nation_key", how="left")
        .join(df_r, on="region_key", how="left")
        .rename({"region_name": "customer_region"})
        .select(["cust_key", "cust_name", "nation_key", "nation_name", "region_key", "customer_region", "acct_bal", "mkt_segment"])
        .to_arrow()
    )

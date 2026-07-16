import bauplan


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


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model()
def customer_with_region(
    customer=bauplan.Model("customer"),
    nation=bauplan.Model("nation"),
    region=bauplan.Model("region"),
):
    """Enriches customer with nation and region via stable reference joins."""
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

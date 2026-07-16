import bauplan


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def orders(
    bronze_orders=bauplan.Model(
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
    """
    Silver base model for orders.
    Grain: one row per order header (orderkey).

    Returned table:
    | orderkey | custkey | orderstatus | totalprice | orderdate | orderpriority | clerk | shippriority |
    """
    import polars as pl

    return (
        pl.DataFrame(bronze_orders)
        .rename(
            {
                "o_orderkey": "orderkey",
                "o_custkey": "custkey",
                "o_orderstatus": "orderstatus",
                "o_totalprice": "totalprice",
                "o_orderdate": "orderdate",
                "o_orderpriority": "orderpriority",
                "o_clerk": "clerk",
                "o_shippriority": "shippriority",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def customer(
    bronze_customer=bauplan.Model(
        "tpch_1.customer",
        columns=[
            "c_custkey",
            "c_name",
            "c_address",
            "c_nationkey",
            "c_phone",
            "c_acctbal",
            "c_mktsegment",
        ],
    ),
):
    """
    Silver base model for customers.
    Grain: one row per customer (custkey).

    Returned table:
    | custkey | name | address | nationkey | phone | acctbal | mktsegment |
    """
    import polars as pl

    return (
        pl.DataFrame(bronze_customer)
        .rename(
            {
                "c_custkey": "custkey",
                "c_name": "name",
                "c_address": "address",
                "c_nationkey": "nationkey",
                "c_phone": "phone",
                "c_acctbal": "acctbal",
                "c_mktsegment": "mktsegment",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def nation(
    bronze_nation=bauplan.Model(
        "tpch_1.nation",
        columns=["n_nationkey", "n_name", "n_regionkey"],
    ),
):
    """
    Silver base model for nations.
    Grain: one row per nation (nationkey).

    Returned table:
    | nationkey | name | regionkey |
    """
    import polars as pl

    return (
        pl.DataFrame(bronze_nation)
        .rename(
            {
                "n_nationkey": "nationkey",
                "n_name": "name",
                "n_regionkey": "regionkey",
            }
        )
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def region(
    bronze_region=bauplan.Model(
        "tpch_1.region",
        columns=["r_regionkey", "r_name"],
    ),
):
    """
    Silver base model for regions.
    Grain: one row per region (regionkey).

    Returned table:
    | regionkey | name |
    """
    import polars as pl

    return (
        pl.DataFrame(bronze_region)
        .rename({"r_regionkey": "regionkey", "r_name": "name"})
        .to_arrow()
    )


@bauplan.python("3.12", pip={"polars": "1.37"})
@bauplan.model(materialization_strategy="REPLACE")
def customer_with_region(
    silver_customer=bauplan.Model("customer", columns=["custkey", "name", "nationkey"]),
    silver_nation=bauplan.Model("nation", columns=["nationkey", "name", "regionkey"]),
    silver_region=bauplan.Model("region", columns=["regionkey", "name"]),
):
    """
    Enriched silver model: customer with resolved customer region.
    Joins customer -> nation -> region (all silver-to-silver).
    Grain: one row per customer (custkey).

    Returned table:
    | custkey | customer_name | nationkey | nation_name | regionkey | customer_region |
    """
    import polars as pl

    cust = pl.DataFrame(silver_customer)
    nat = pl.DataFrame(silver_nation)
    reg = pl.DataFrame(silver_region)

    return (
        cust.rename({"name": "customer_name"})
        .join(
            nat.rename({"name": "nation_name"}),
            on="nationkey",
            how="inner",
        )
        .join(
            reg.rename({"name": "customer_region"}),
            on="regionkey",
            how="inner",
        )
        .select(
            [
                "custkey",
                "customer_name",
                "nationkey",
                "nation_name",
                "regionkey",
                "customer_region",
            ]
        )
        .to_arrow()
    )

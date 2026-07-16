import bauplan
from bauplan.standard_expectations import (
    expect_column_accepted_values,
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_unique(
    data=bauplan.Model("orders", columns=["orderkey"]),
):
    return expect_column_all_unique(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_no_nulls(
    data=bauplan.Model("orders", columns=["orderkey"]),
):
    return expect_column_no_nulls(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_custkey_no_nulls(
    data=bauplan.Model("orders", columns=["custkey"]),
):
    return expect_column_no_nulls(data, "custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_custkey_unique(
    data=bauplan.Model("customer", columns=["custkey"]),
):
    return expect_column_all_unique(data, "custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_custkey_no_nulls(
    data=bauplan.Model("customer", columns=["custkey"]),
):
    return expect_column_no_nulls(data, "custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_nationkey_no_nulls(
    data=bauplan.Model("customer", columns=["nationkey"]),
):
    return expect_column_no_nulls(data, "nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_nationkey_unique(
    data=bauplan.Model("nation", columns=["nationkey"]),
):
    return expect_column_all_unique(data, "nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_nationkey_no_nulls(
    data=bauplan.Model("nation", columns=["nationkey"]),
):
    return expect_column_no_nulls(data, "nationkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_regionkey_unique(
    data=bauplan.Model("region", columns=["regionkey"]),
):
    return expect_column_all_unique(data, "regionkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_regionkey_no_nulls(
    data=bauplan.Model("region", columns=["regionkey"]),
):
    return expect_column_no_nulls(data, "regionkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_custkey_unique(
    data=bauplan.Model("customer_with_region", columns=["custkey"]),
):
    return expect_column_all_unique(data, "custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_custkey_no_nulls(
    data=bauplan.Model("customer_with_region", columns=["custkey"]),
):
    return expect_column_no_nulls(data, "custkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_region_no_nulls(
    data=bauplan.Model("customer_with_region", columns=["customer_region"]),
):
    return expect_column_no_nulls(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_accepted_regions(
    data=bauplan.Model("customer_with_region", columns=["customer_region"]),
):
    return expect_column_accepted_values(
        data,
        "customer_region",
        ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"],
    )

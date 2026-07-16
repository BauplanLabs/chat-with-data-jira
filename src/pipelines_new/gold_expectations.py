import bauplan
from bauplan.standard_expectations import (
    expect_column_no_nulls,
    expect_column_all_unique,
    expect_column_accepted_values,
)

_VALID_REGIONS = ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"]


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_no_null_region(
    data=bauplan.Model("orders_by_customer_region", columns=["customer_region"]),
):
    return expect_column_no_nulls(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_no_null_count(
    data=bauplan.Model("orders_by_customer_region", columns=["order_count"]),
):
    return expect_column_no_nulls(data, "order_count")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_unique_regions(
    data=bauplan.Model("orders_by_customer_region", columns=["customer_region"]),
):
    return expect_column_all_unique(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_by_region_accepted_regions(
    data=bauplan.Model("orders_by_customer_region", columns=["customer_region"]),
):
    return expect_column_accepted_values(data, "customer_region", _VALID_REGIONS)

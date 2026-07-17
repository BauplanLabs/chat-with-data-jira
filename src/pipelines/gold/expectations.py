import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
    expect_column_mean_greater_than,
)


@bauplan.expectation()
@bauplan.python("3.12")
def test_revenue_by_customer_region_region_unique(
    data=bauplan.Model("revenue_by_customer_region", columns=["customer_region"]),
):
    """Each region appears exactly once in the output."""
    return expect_column_all_unique(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_revenue_by_customer_region_region_not_null(
    data=bauplan.Model("revenue_by_customer_region", columns=["customer_region"]),
):
    """No null region values — every line item maps to a customer region."""
    return expect_column_no_nulls(data, "customer_region")


@bauplan.expectation()
@bauplan.python("3.12")
def test_revenue_by_customer_region_net_revenue_positive(
    data=bauplan.Model("revenue_by_customer_region", columns=["net_revenue"]),
):
    """Net revenue is positive for every region."""
    return expect_column_mean_greater_than(data, "net_revenue", 0)

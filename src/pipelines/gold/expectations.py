import bauplan
from bauplan.standard_expectations import (
    expect_column_accepted_values,
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_no_null_region(
    data=bauplan.Model('revenue_by_customer_region', columns=['region_name']),
):
    """Output must have a region name for every row."""
    return expect_column_no_nulls(data, 'region_name')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_unique_regions(
    data=bauplan.Model('revenue_by_customer_region', columns=['region_name']),
):
    """One row per region — no duplicates."""
    return expect_column_all_unique(data, 'region_name')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_known_regions(
    data=bauplan.Model('revenue_by_customer_region', columns=['region_name']),
):
    """Only the five TPC-H regions are valid values."""
    return expect_column_accepted_values(
        data,
        'region_name',
        ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST'],
    )


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_no_null_net_revenue(
    data=bauplan.Model('revenue_by_customer_region', columns=['net_revenue']),
):
    """Net revenue must be present for every region."""
    return expect_column_no_nulls(data, 'net_revenue')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_positive_net_revenue(
    data=bauplan.Model('revenue_by_customer_region', columns=['net_revenue']),
):
    """Mean net revenue across regions must be positive."""
    return expect_column_mean_greater_than(data, 'net_revenue', 0.0)


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_no_null_order_count(
    data=bauplan.Model('revenue_by_customer_region', columns=['order_count']),
):
    """Order count must be present for every region."""
    return expect_column_no_nulls(data, 'order_count')

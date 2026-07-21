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
    data=bauplan.Model('net_revenue_by_customer_region', columns=['region']),
):
    """Every output row must have a region name."""
    return expect_column_no_nulls(data, 'region')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_unique_regions(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['region']),
):
    """One row per region — duplicates would misrepresent the geography slide."""
    return expect_column_all_unique(data, 'region')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_known_regions(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['region']),
):
    """Only the five canonical TPC-H customer regions are valid."""
    return expect_column_accepted_values(
        data,
        'region',
        ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST'],
    )


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_no_null_net_revenue(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    """Net revenue must be populated for every region."""
    return expect_column_no_nulls(data, 'net_revenue')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_positive_net_revenue(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    """Mean net revenue across regions must be positive — negative would indicate a data error."""
    return expect_column_mean_greater_than(data, 'net_revenue', 0.0)


@bauplan.expectation()
@bauplan.python('3.12')
def expect_gold_no_null_orders(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['orders']),
):
    """Order count must be present for every region."""
    return expect_column_no_nulls(data, 'orders')

import bauplan
from bauplan.standard_expectations import (
    expect_column_accepted_values,
    expect_column_no_nulls,
    expect_column_mean_greater_than,
)

_REGIONS = ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST']


@bauplan.expectation()
@bauplan.python('3.11')
def expect_revenue_by_region_no_nulls(
    data=bauplan.Model(
        'revenue_by_customer_region',
        columns=['region', 'net_revenue'],
    ),
):
    """Both output columns are fully populated."""
    return expect_column_no_nulls(data, 'region') and expect_column_no_nulls(
        data, 'net_revenue'
    )


@bauplan.expectation()
@bauplan.python('3.11')
def expect_revenue_by_region_valid_regions(
    data=bauplan.Model(
        'revenue_by_customer_region',
        columns=['region'],
    ),
):
    """Region column contains only the five TPC-H geographic regions."""
    return expect_column_accepted_values(data, 'region', _REGIONS)


@bauplan.expectation()
@bauplan.python('3.11')
def expect_revenue_by_region_positive(
    data=bauplan.Model(
        'revenue_by_customer_region',
        columns=['net_revenue'],
    ),
):
    """Net revenue is positive for every region (no zero or negative totals)."""
    return expect_column_mean_greater_than(data, 'net_revenue', 0.0)

import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_no_null_region(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    return expect_column_no_nulls(data, 'customer_region')


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_unique_region(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['customer_region']),
):
    return expect_column_all_unique(data, 'customer_region')


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_no_null_net_revenue(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    return expect_column_no_nulls(data, 'net_revenue')


@bauplan.expectation()
@bauplan.python('3.12')
def test_gold_positive_net_revenue(
    data=bauplan.Model('net_revenue_by_customer_region', columns=['net_revenue']),
):
    return expect_column_mean_greater_than(data, 'net_revenue', 0)

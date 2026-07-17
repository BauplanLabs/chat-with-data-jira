import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_by_region_no_null_region(
    data=bauplan.Model('orders_by_region', columns=['region']),
):
    return expect_column_no_nulls(data, 'region')


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_by_region_no_null_count(
    data=bauplan.Model('orders_by_region', columns=['order_count']),
):
    return expect_column_no_nulls(data, 'order_count')


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_by_region_unique_region(
    data=bauplan.Model('orders_by_region', columns=['region']),
):
    return expect_column_all_unique(data, 'region')

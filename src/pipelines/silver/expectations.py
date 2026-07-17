import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_no_null_order_key(
    data=bauplan.Model('lineitem', columns=['order_key']),
):
    return expect_column_no_nulls(data, 'order_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_lineitem_no_null_extended_price(
    data=bauplan.Model('lineitem', columns=['extended_price']),
):
    return expect_column_no_nulls(data, 'extended_price')


@bauplan.expectation()
@bauplan.python('3.12')
def test_orders_no_null_order_key(
    data=bauplan.Model('orders', columns=['order_key']),
):
    return expect_column_no_nulls(data, 'order_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_orders_unique_order_key(
    data=bauplan.Model('orders', columns=['order_key']),
):
    return expect_column_all_unique(data, 'order_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customer_no_null_customer_key(
    data=bauplan.Model('customer', columns=['customer_key']),
):
    return expect_column_no_nulls(data, 'customer_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customer_unique_customer_key(
    data=bauplan.Model('customer', columns=['customer_key']),
):
    return expect_column_all_unique(data, 'customer_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_nation_no_null_nation_key(
    data=bauplan.Model('nation', columns=['nation_key']),
):
    return expect_column_no_nulls(data, 'nation_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_region_no_null_region_key(
    data=bauplan.Model('region', columns=['region_key']),
):
    return expect_column_no_nulls(data, 'region_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_region_no_null_region_name(
    data=bauplan.Model('region', columns=['region_name']),
):
    return expect_column_no_nulls(data, 'region_name')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_no_null_customer_key(
    data=bauplan.Model('customers_with_region', columns=['customer_key']),
):
    return expect_column_no_nulls(data, 'customer_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_unique_customer_key(
    data=bauplan.Model('customers_with_region', columns=['customer_key']),
):
    return expect_column_all_unique(data, 'customer_key')


@bauplan.expectation()
@bauplan.python('3.12')
def test_customers_with_region_no_null_region(
    data=bauplan.Model('customers_with_region', columns=['customer_region']),
):
    return expect_column_no_nulls(data, 'customer_region')

import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_no_null_orderkey(
    data=bauplan.Model('orders', columns=['o_orderkey']),
):
    return expect_column_no_nulls(data, 'o_orderkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_orders_no_null_custkey(
    data=bauplan.Model('orders', columns=['o_custkey']),
):
    return expect_column_no_nulls(data, 'o_custkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customer_no_null_custkey(
    data=bauplan.Model('customer', columns=['c_custkey']),
):
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_nation_no_null_nationkey(
    data=bauplan.Model('nation', columns=['n_nationkey']),
):
    return expect_column_no_nulls(data, 'n_nationkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_region_no_null_regionkey(
    data=bauplan.Model('region', columns=['r_regionkey']),
):
    return expect_column_no_nulls(data, 'r_regionkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_region_no_null_name(
    data=bauplan.Model('region', columns=['r_name']),
):
    return expect_column_no_nulls(data, 'r_name')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customers_with_region_no_null_custkey(
    data=bauplan.Model('customers_with_region', columns=['c_custkey']),
):
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customers_with_region_no_null_region(
    data=bauplan.Model('customers_with_region', columns=['region']),
):
    return expect_column_no_nulls(data, 'region')


@bauplan.expectation()
@bauplan.python('3.11')
def test_customers_with_region_unique_custkey(
    data=bauplan.Model('customers_with_region', columns=['c_custkey']),
):
    return expect_column_all_unique(data, 'c_custkey')

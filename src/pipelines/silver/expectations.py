import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.11')
def expect_lineitem(
    data=bauplan.Model(
        'lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
):
    assert expect_column_no_nulls(data, 'l_orderkey'), 'l_orderkey has nulls'
    assert expect_column_no_nulls(data, 'l_extendedprice'), 'l_extendedprice has nulls'
    assert expect_column_no_nulls(data, 'l_discount'), 'l_discount has nulls'
    return True


@bauplan.expectation()
@bauplan.python('3.11')
def expect_orders(
    data=bauplan.Model('orders', columns=['o_orderkey', 'o_custkey']),
):
    assert expect_column_no_nulls(data, 'o_orderkey'), 'o_orderkey has nulls'
    assert expect_column_no_nulls(data, 'o_custkey'), 'o_custkey has nulls'
    assert expect_column_all_unique(data, 'o_orderkey'), 'o_orderkey is not unique'
    return True


@bauplan.expectation()
@bauplan.python('3.11')
def expect_customer(
    data=bauplan.Model('customer', columns=['c_custkey', 'c_nationkey']),
):
    assert expect_column_no_nulls(data, 'c_custkey'), 'c_custkey has nulls'
    assert expect_column_no_nulls(data, 'c_nationkey'), 'c_nationkey has nulls'
    assert expect_column_all_unique(data, 'c_custkey'), 'c_custkey is not unique'
    return True


@bauplan.expectation()
@bauplan.python('3.11')
def expect_nation(
    data=bauplan.Model('nation', columns=['n_nationkey', 'n_regionkey']),
):
    assert expect_column_no_nulls(data, 'n_nationkey'), 'n_nationkey has nulls'
    assert expect_column_no_nulls(data, 'n_regionkey'), 'n_regionkey has nulls'
    assert expect_column_all_unique(data, 'n_nationkey'), 'n_nationkey is not unique'
    return True


@bauplan.expectation()
@bauplan.python('3.11')
def expect_region(
    data=bauplan.Model('region', columns=['r_regionkey', 'r_name']),
):
    assert expect_column_no_nulls(data, 'r_regionkey'), 'r_regionkey has nulls'
    assert expect_column_no_nulls(data, 'r_name'), 'r_name has nulls'
    assert expect_column_all_unique(data, 'r_regionkey'), 'r_regionkey is not unique'
    return True


@bauplan.expectation()
@bauplan.python('3.11')
def expect_nation_region(
    data=bauplan.Model(
        'nation_region',
        columns=['n_nationkey', 'n_name', 'r_name'],
    ),
):
    assert expect_column_no_nulls(data, 'n_nationkey'), 'n_nationkey has nulls'
    assert expect_column_no_nulls(data, 'r_name'), 'r_name has nulls'
    assert expect_column_all_unique(data, 'n_nationkey'), 'n_nationkey is not unique in nation_region'
    return True

import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.12')
def expect_lineitem_no_null_orderkeys(
    data=bauplan.Model('lineitem', columns=['l_orderkey']),
):
    """Every line item must reference an order — l_orderkey is the join key for revenue rollup."""
    return expect_column_no_nulls(data, 'l_orderkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_lineitem_no_null_extendedprice(
    data=bauplan.Model('lineitem', columns=['l_extendedprice']),
):
    """Extended price must be present; net revenue cannot be computed without it."""
    return expect_column_no_nulls(data, 'l_extendedprice')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_lineitem_no_null_discount(
    data=bauplan.Model('lineitem', columns=['l_discount']),
):
    """Discount must be present; net revenue formula is extendedprice * (1 - discount)."""
    return expect_column_no_nulls(data, 'l_discount')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_orders_no_null_orderkeys(
    data=bauplan.Model('orders', columns=['o_orderkey']),
):
    """Every order must have a primary key for joining to line items."""
    return expect_column_no_nulls(data, 'o_orderkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_orders_no_null_custkeys(
    data=bauplan.Model('orders', columns=['o_custkey']),
):
    """Every order must reference a customer — needed to resolve customer region."""
    return expect_column_no_nulls(data, 'o_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_customer_no_null_custkeys(
    data=bauplan.Model('customer', columns=['c_custkey']),
):
    """Customer primary key must be present for join integrity."""
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_nation_unique_keys(
    data=bauplan.Model('nation', columns=['n_nationkey']),
):
    """Nation lookup must have unique keys — duplicate nations would fan out the geography join."""
    return expect_column_all_unique(data, 'n_nationkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_region_unique_keys(
    data=bauplan.Model('region', columns=['r_regionkey']),
):
    """Region lookup must have unique keys — TPC-H has exactly five regions."""
    return expect_column_all_unique(data, 'r_regionkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_customer_geography_no_null_custkey(
    data=bauplan.Model('customer_geography', columns=['c_custkey']),
):
    """Every row in the enriched geography table must have a customer key."""
    return expect_column_no_nulls(data, 'c_custkey')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_customer_geography_no_null_region(
    data=bauplan.Model('customer_geography', columns=['region_name']),
):
    """Every customer must resolve to a region — a null signals a broken geography join."""
    return expect_column_no_nulls(data, 'region_name')


@bauplan.expectation()
@bauplan.python('3.12')
def expect_customer_geography_unique_custkeys(
    data=bauplan.Model('customer_geography', columns=['c_custkey']),
):
    """Customer geography must be one row per customer — fan-out would double-count revenue."""
    return expect_column_all_unique(data, 'c_custkey')

import bauplan
from bauplan.standard_expectations import (
    expect_column_no_nulls,
    expect_column_mean_greater_than,
)


@bauplan.expectation()
@bauplan.python('3.11')
def expect_lineitem_no_nulls(
    data=bauplan.Model(
        'lineitem',
        columns=['l_orderkey', 'l_extendedprice', 'l_discount'],
    ),
):
    """All join and revenue columns on lineitem are populated."""
    return (
        expect_column_no_nulls(data, 'l_orderkey')
        and expect_column_no_nulls(data, 'l_extendedprice')
        and expect_column_no_nulls(data, 'l_discount')
    )


@bauplan.expectation()
@bauplan.python('3.11')
def expect_lineitem_prices_positive(
    data=bauplan.Model(
        'lineitem',
        columns=['l_extendedprice'],
    ),
):
    """Extended price is always positive (no zero or negative line values)."""
    return expect_column_mean_greater_than(data, 'l_extendedprice', 0.0)


@bauplan.expectation()
@bauplan.python('3.11')
def expect_orders_no_nulls(
    data=bauplan.Model(
        'orders',
        columns=['o_orderkey', 'o_custkey'],
    ),
):
    """Order key and customer key on orders are populated."""
    return expect_column_no_nulls(data, 'o_orderkey') and expect_column_no_nulls(
        data, 'o_custkey'
    )


@bauplan.expectation()
@bauplan.python('3.11')
def expect_customer_no_nulls(
    data=bauplan.Model(
        'customer',
        columns=['c_custkey', 'c_nationkey'],
    ),
):
    """Customer key and nation key are populated."""
    return expect_column_no_nulls(data, 'c_custkey') and expect_column_no_nulls(
        data, 'c_nationkey'
    )


@bauplan.expectation()
@bauplan.python('3.11')
def expect_nation_no_nulls(
    data=bauplan.Model(
        'nation',
        columns=['n_nationkey', 'n_regionkey'],
    ),
):
    """Nation key and region key are populated."""
    return expect_column_no_nulls(data, 'n_nationkey') and expect_column_no_nulls(
        data, 'n_regionkey'
    )


@bauplan.expectation()
@bauplan.python('3.11')
def expect_region_no_nulls(
    data=bauplan.Model(
        'region',
        columns=['r_regionkey', 'r_name'],
    ),
):
    """Region key and region name are populated."""
    return expect_column_no_nulls(data, 'r_regionkey') and expect_column_no_nulls(
        data, 'r_name'
    )


@bauplan.expectation()
@bauplan.python('3.11')
def expect_customer_with_region_no_nulls(
    data=bauplan.Model(
        'customer_with_region',
        columns=['c_custkey', 'region_name'],
    ),
):
    """Every customer maps to a region (no orphan customers after the join)."""
    return expect_column_no_nulls(data, 'c_custkey') and expect_column_no_nulls(
        data, 'region_name'
    )

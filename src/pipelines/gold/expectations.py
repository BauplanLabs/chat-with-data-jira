import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_mean_greater_than,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python('3.11')
def expect_net_revenue_by_customer_region(
    data=bauplan.Model(
        'net_revenue_by_customer_region',
        columns=['region', 'net_revenue', 'order_count'],
    ),
):
    assert expect_column_no_nulls(data, 'region'), 'region has nulls'
    assert expect_column_no_nulls(data, 'net_revenue'), 'net_revenue has nulls'
    assert expect_column_no_nulls(data, 'order_count'), 'order_count has nulls'
    assert expect_column_all_unique(data, 'region'), 'region is not unique — expected one row per region'
    assert expect_column_mean_greater_than(data, 'net_revenue', 0.0), 'mean net_revenue is not positive'
    return True

import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
    expect_column_mean_greater_than,
)


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_order_key_not_null(
    data=bauplan.Model("lineitem", columns=["order_key"]),
):
    """Every line item references an order."""
    return expect_column_no_nulls(data, "order_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_extended_price_positive(
    data=bauplan.Model("lineitem", columns=["extended_price"]),
):
    """Extended price is positive for all line items."""
    return expect_column_mean_greater_than(data, "extended_price", 0)


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_discount_not_null(
    data=bauplan.Model("lineitem", columns=["discount"]),
):
    """Discount is present on every line item."""
    return expect_column_no_nulls(data, "discount")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_order_key_unique(
    data=bauplan.Model("orders", columns=["order_key"]),
):
    """Every order has a unique primary key."""
    return expect_column_all_unique(data, "order_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_cust_key_not_null(
    data=bauplan.Model("orders", columns=["cust_key"]),
):
    """Every order references a customer."""
    return expect_column_no_nulls(data, "cust_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_cust_key_unique(
    data=bauplan.Model("customer", columns=["cust_key"]),
):
    """Customer primary key is unique."""
    return expect_column_all_unique(data, "cust_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_nation_key_not_null(
    data=bauplan.Model("customer", columns=["nation_key"]),
):
    """Every customer is assigned to a nation."""
    return expect_column_no_nulls(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_nation_key_unique(
    data=bauplan.Model("nation", columns=["nation_key"]),
):
    """Nation primary key is unique."""
    return expect_column_all_unique(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_region_key_unique(
    data=bauplan.Model("region", columns=["region_key"]),
):
    """Region primary key is unique."""
    return expect_column_all_unique(data, "region_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_cust_key_unique(
    data=bauplan.Model("customer_with_region", columns=["cust_key"]),
):
    """Enriched customer table preserves one row per customer."""
    return expect_column_all_unique(data, "cust_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_with_region_customer_region_not_null(
    data=bauplan.Model("customer_with_region", columns=["customer_region"]),
):
    """Every customer has a resolved customer region after the join."""
    return expect_column_no_nulls(data, "customer_region")

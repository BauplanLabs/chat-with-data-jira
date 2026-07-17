import bauplan
from bauplan.standard_expectations import (
    expect_column_all_unique,
    expect_column_no_nulls,
)


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_orderkey_no_nulls(
    data=bauplan.Model("lineitem", columns=["orderkey"]),
):
    """No null order keys on lineitem — every line item must belong to an order."""
    return expect_column_no_nulls(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_extended_price_no_nulls(
    data=bauplan.Model("lineitem", columns=["extended_price"]),
):
    """No null extended prices — required for net revenue computation."""
    return expect_column_no_nulls(data, "extended_price")


@bauplan.expectation()
@bauplan.python("3.12")
def test_lineitem_discount_no_nulls(
    data=bauplan.Model("lineitem", columns=["discount"]),
):
    """No null discounts — required for net revenue computation."""
    return expect_column_no_nulls(data, "discount")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_no_nulls(
    data=bauplan.Model("orders", columns=["orderkey"]),
):
    """No null order keys on orders header table."""
    return expect_column_no_nulls(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_orderkey_unique(
    data=bauplan.Model("orders", columns=["orderkey"]),
):
    """Order key is the primary key of the orders table — must be unique."""
    return expect_column_all_unique(data, "orderkey")


@bauplan.expectation()
@bauplan.python("3.12")
def test_orders_customer_key_no_nulls(
    data=bauplan.Model("orders", columns=["customer_key"]),
):
    """Every order must reference a customer."""
    return expect_column_no_nulls(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_key_no_nulls(
    data=bauplan.Model("customer", columns=["customer_key"]),
):
    """No null customer keys."""
    return expect_column_no_nulls(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_key_unique(
    data=bauplan.Model("customer", columns=["customer_key"]),
):
    """Customer key is the primary key — must be unique."""
    return expect_column_all_unique(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customer_nation_key_no_nulls(
    data=bauplan.Model("customer", columns=["nation_key"]),
):
    """Every customer must belong to a nation."""
    return expect_column_no_nulls(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_key_no_nulls(
    data=bauplan.Model("nation", columns=["nation_key"]),
):
    """No null nation keys."""
    return expect_column_no_nulls(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_nation_key_unique(
    data=bauplan.Model("nation", columns=["nation_key"]),
):
    """Nation key is the primary key — must be unique."""
    return expect_column_all_unique(data, "nation_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_key_no_nulls(
    data=bauplan.Model("region", columns=["region_key"]),
):
    """No null region keys."""
    return expect_column_no_nulls(data, "region_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_region_key_unique(
    data=bauplan.Model("region", columns=["region_key"]),
):
    """Region key is the primary key — must be unique."""
    return expect_column_all_unique(data, "region_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customers_geo_customer_key_no_nulls(
    data=bauplan.Model("customers_geo", columns=["customer_key"]),
):
    """No null customer keys in the geography lookup."""
    return expect_column_no_nulls(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customers_geo_customer_key_unique(
    data=bauplan.Model("customers_geo", columns=["customer_key"]),
):
    """Geography lookup is one-row-per-customer — customer key must be unique."""
    return expect_column_all_unique(data, "customer_key")


@bauplan.expectation()
@bauplan.python("3.12")
def test_customers_geo_region_name_no_nulls(
    data=bauplan.Model("customers_geo", columns=["region_name"]),
):
    """Every customer must map to a region — no null region names."""
    return expect_column_no_nulls(data, "region_name")

# Gold layer expectations.
# The actual bauplan-decorated expectation functions are defined in the root models.py.
#
# Expectations covering net_revenue_by_customer_region:
#   customer_region – no null, unique (one row per region), accepted values (5 TPC-H regions)
#   net_revenue     – no null, positive mean
#   orders          – no null

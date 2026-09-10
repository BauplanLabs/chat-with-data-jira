# Gold pipeline model implementations.
# The actual bauplan-decorated functions are defined in the root models.py
# and organized here for reference only.
#
# Gold models:
#   net_revenue_by_customer_region
#       Grain : one row per customer region (5 rows)
#       Inputs: lineitem (silver), orders (silver), customers_with_region (silver enriched)
#       Metrics:
#           net_revenue – SUM(l_extendedprice * (1 - l_discount)), pre-tax net revenue
#           orders      – COUNT(DISTINCT o_orderkey), distinct order headers per region
#       Materialization: REPLACE

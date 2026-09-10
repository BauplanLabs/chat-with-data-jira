# Silver pipeline model implementations.
# The actual bauplan-decorated functions are defined in the root models.py.
#
# Silver base models:
#   lineitem           – tpch_1.lineitem (6M rows): l_orderkey, l_extendedprice, l_discount
#   orders             – tpch_1.orders (1.5M rows): o_orderkey, o_custkey
#   customer           – tpch_1.customer (150K rows): c_custkey, c_nationkey
#   nation             – tpch_1.nation (25 rows): n_nationkey, n_regionkey
#   region             – tpch_1.region (5 rows): r_regionkey, r_name
#
# Silver enriched models:
#   customer_with_region – customer joined to nation and region; grain: c_custkey
#                          exposes: c_custkey, customer_region (r_name)

# Silver layer expectations.
# The actual bauplan-decorated expectation functions are defined in the root models.py.
#
# Expectations covering:
#   lineitem           – no null l_orderkey, l_extendedprice, l_discount; positive mean price
#   orders             – no null o_orderkey, o_custkey; o_orderkey unique
#   customer           – no null c_custkey, c_nationkey; c_custkey unique
#   nation             – n_nationkey unique; no null n_regionkey
#   region             – r_regionkey unique; r_name in accepted values
#   customers_with_region – c_custkey no null + unique; customer_region no null + accepted values

# Silver pipeline model implementations.
# The actual bauplan-decorated functions are defined in the root models.py
# and organized here for reference only.
#
# Silver base models:
#   lineitem           – tpch_1.lineitem (6M rows): order key, price, discount, dates, flags
#   orders             – tpch_1.orders (1.5M rows): order key, customer key, status, dates
#   customer           – tpch_1.customer (150K rows): customer key, nation key, segment
#   nation             – tpch_1.nation (25 rows): nation key, name, region key
#   region             – tpch_1.region (5 rows): region key, name
#
# Silver enriched models:
#   customers_with_region – customer joined to nation and region; grain: c_custkey
#                           exposes: c_custkey, customer_region

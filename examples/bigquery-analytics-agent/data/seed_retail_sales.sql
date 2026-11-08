-- Materialize a small, fixed 2024 slice of Google Cloud's synthetic
-- bigquery-public-data.thelook_ecommerce dataset.
-- The destination table is supplied by scripts/seed.sh.
SELECT
  oi.id AS order_item_id,
  oi.order_id,
  oi.status AS order_status,
  oi.created_at AS order_created_at,
  oi.shipped_at,
  oi.delivered_at,
  oi.returned_at,
  ROUND(oi.sale_price, 2) AS sale_price,
  ROUND(p.cost, 2) AS product_cost,
  ROUND(oi.sale_price - p.cost, 2) AS gross_margin,
  p.category AS product_category,
  p.name AS product_name,
  p.brand,
  p.department,
  u.age AS customer_age,
  u.gender AS customer_gender,
  u.country AS customer_country,
  u.state AS customer_state,
  u.traffic_source
FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
JOIN `bigquery-public-data.thelook_ecommerce.products` AS p
  ON p.id = oi.product_id
JOIN `bigquery-public-data.thelook_ecommerce.users` AS u
  ON u.id = oi.user_id
WHERE oi.created_at >= TIMESTAMP("2024-01-01")
  AND oi.created_at < TIMESTAMP("2025-01-01")

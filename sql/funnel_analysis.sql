CREATE DATABASE my_database;

USE my_database;
SELECT * FROM user_events Limit 1000; 


-- define sales funnel and the diffrent stages
-- creates a temporary result set named funnel_stages that calculates user counts across distinct funnel stages

-- CTE
-- What is a Common Table Expression (CTE)?
-- A CTE (created using the WITH clause) creates a temporary named result set (like a temporary virtual table) that you can reference within your main SELECT, INSERT, UPDATE, or DELETE query.

-- Purpose: It helps break down complex queries into modular, readable chunks instead of writing multiple nested subqueries.
WITH funnel_stages AS (
SELECT 
COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END ) AS stage_1_views,
COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN user_id END ) AS stage_2_cart,
COUNT(DISTINCT CASE WHEN event_type = 'checkout_start' THEN user_id END ) AS stage_3_checkout,
COUNT(DISTINCT CASE WHEN event_type = 'payment_info' THEN user_id END ) AS stage_4_payment,
COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END ) AS stage_5_purchase


FROM user_events

-- analysis for last 30 days data
-- WHERE event_date >= TIMESTAMP(DATE_SUB(CURRENT_DATE(),INTERVAL 30 DAY))
WHERE event_date >= (SELECT MAX(event_date) FROM user_events) - INTERVAL 30 DAY

)


-- funnel is decriasing with every stage

-- conversion rate through the funnel 

SELECT 
stage_1_views,
stage_2_cart,
ROUND(stage_2_cart * 100 / stage_1_views,2) as view_to_cart_rate,

stage_3_checkout,
ROUND(stage_3_checkout * 100 / stage_2_cart,2) as cart_to_checkout_rate,

stage_4_payment,
ROUND(stage_4_payment * 100 / stage_3_checkout,2) as checkout_to_payment_rate,

stage_5_purchase,
ROUND(stage_5_purchase * 100 / stage_4_payment,2) as payment_to_purchase_rate,

ROUND(stage_5_purchase * 100 / stage_1_views,2) as overall_rate

FROM funnel_stages;

-- payment to purchase rate is good, mojor problem is from view to cart people are browsing, we should go for wbsite/interface exp  


-- funnel with source


WITH source_funnel AS (
SELECT traffic_source,
COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END ) AS views,
COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN user_id END ) AS carts,
COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END ) AS purchase
FROM user_events

WHERE event_date >= (SELECT MAX(event_date) FROM user_events) - INTERVAL 30 DAY

GROUP BY traffic_source
)

SELECT
traffic_source,
views,
carts,
purchase,
ROUND(carts * 100 / views,2) as cart_conversion_rate,
ROUND( purchase * 100 / views,2) as cart_conversion_rate,
ROUND(purchase * 100 / carts,2) as cart_to_purchase_conversion_rate
FROM source_funnel
ORDER BY purchase desc;


-- time spent to conversion analysis
WITH user_journey AS (
SELECT user_id,
MIN(CASE WHEN event_type = 'page_view' THEN event_date END ) AS views_time,
MIN(CASE WHEN event_type = 'add_to_cart' THEN event_date END ) AS carts_time,
MIN(CASE WHEN event_type = 'purchase' THEN event_date END ) AS purchase_time
FROM user_events

WHERE event_date >= (SELECT MAX(event_date) FROM user_events) - INTERVAL 30 DAY

GROUP BY user_id
-- actual purchase happend
HAVING MIN(CASE WHEN event_type = 'purchase' THEN event_date END ) is not null


)


SELECT
  COUNT(*) AS converted_users,
  ROUND(AVG(TIMESTAMPDIFF(MINUTE, views_time, carts_time)), 2) AS avg_view_to_cart_mins,
  ROUND(AVG(TIMESTAMPDIFF(MINUTE, carts_time, purchase_time)), 2) AS avg_cart_to_purchase_mins,
  ROUND(AVG(TIMESTAMPDIFF(MINUTE, views_time, purchase_time)), 2) AS avg_total_journey_mins
FROM user_journey;



-- revenue funnel

WITH revenue_funnel AS (
SELECT
COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END ) AS total_visitors,
COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END ) AS total_buyers,
ROUND(SUM(CASE WHEN event_type = 'purchase' THEN amount END),2) AS total_revenue,
COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS total_orders
FROM user_events

WHERE event_date >= (SELECT MAX(event_date) FROM user_events) - INTERVAL 30 DAY

)
SELECT
total_visitors,
total_buyers,
total_revenue,
total_orders,
ROUND(total_revenue/total_orders,2) AS avg_order_value,
ROUND(total_revenue/total_buyers,2) AS revenue_per_buyer,
ROUND(total_revenue/total_visitors,2) AS revenue_per_visitior
FROM revenue_funnel;


-- comparing with CAC if CAC is 50$ but our agv per order is around 107.4 somewhere we are making profits
-- by this we can understand how our marketing efforts are paying of


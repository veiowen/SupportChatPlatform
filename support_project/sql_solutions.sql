
-- ============================================
-- FOOD SUPPORT: SQL TEST ASSIGNMENT
-- SQL Dialect: SQLite
-- ============================================


-- ============================================
-- TASK A
-- Find usernames of clients who gave
-- a CSAT score lower than 3.
-- DISTINCT removes duplicate usernames.
-- ============================================

SELECT DISTINCT
    ticket_client
FROM tickets
WHERE csat < 3;


-- ============================================
-- TASK B
-- Find ticket IDs where the message contains
-- the word "отлично".
-- Sort by CSAT from highest to lowest.
-- ============================================

SELECT
    ticket_id
FROM tickets
WHERE LOWER(text) LIKE '%отлично%'
ORDER BY csat DESC;


-- ============================================
-- TASK C
-- Find clients with more than 5 orders
-- at "Теремок" or "Вкусно и точка".
-- Only orders priced from 2000 to 10000 RUB
-- are included in the calculation.
-- Return each client's ID and highest
-- qualifying order price.
-- ============================================

SELECT
    order_client_id AS frequent_customer,
    MAX(price) AS max_sum
FROM orders
WHERE place IN (
    'Теремок',
    'Вкусно и точка'
)
AND price BETWEEN 2000 AND 10000
GROUP BY order_client_id
HAVING COUNT(*) > 5;


-- ============================================
-- TASK D (BONUS)
-- Enrich orders with information from
-- clients and support tickets.
-- LEFT JOIN retains orders without tickets.
-- Match tickets by order ID and client username.
-- Return no more than 1000 records.
-- ============================================

SELECT
    o.*,
    c.username,
    c.name,
    c.age,
    c.city,
    t.ticket_id,
    t.csat,
    t.text AS ticket_text,
    t.date AS ticket_date
FROM orders AS o
LEFT JOIN clients AS c
    ON o.order_client_id = c.client_id
LEFT JOIN tickets AS t
    ON o.order_id = t.ticket_order_id
    AND c.username = t.ticket_client
ORDER BY o.order_id
LIMIT 1000;

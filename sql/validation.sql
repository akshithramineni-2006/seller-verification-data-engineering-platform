
-- ============================================
-- DATA QUALITY VALIDATION QUERIES
-- ============================================

-- 1. Duplicate Seller IDs
SELECT
    'Duplicate Seller IDs' AS "Check",
    COUNT(*) AS "Count"
FROM (
    SELECT seller_id
    FROM sellers
    GROUP BY seller_id
    HAVING COUNT(*) > 1
) duplicates;

-- 2. Missing Revenue
SELECT
    'Missing Revenue' AS "Check",
    COUNT(*) AS "Count"
FROM sellers
WHERE annual_revenue IS NULL;

-- 3. Missing PAN Status
SELECT
    'Missing PAN Status' AS "Check",
    COUNT(*) AS "Count"
FROM verification
WHERE pan_status IS NULL;

-- 4. Invalid Risk Score
SELECT
    'Invalid Risk Score' AS "Check",
    COUNT(*) AS "Count"
FROM fraud
WHERE risk_score < 0 OR risk_score > 100;

-- 5. Negative Sales
SELECT
    'Negative Sales' AS "Check",
    COUNT(*) AS "Count"
FROM transactions
WHERE sales < 0;

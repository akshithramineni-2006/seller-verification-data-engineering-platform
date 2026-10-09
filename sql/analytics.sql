-- ============================================
-- ANALYTICS QUERIES
-- ============================================


-- 1. Total Sellers
-- Output: total_sellers.csv

SELECT
    COUNT(*) AS total_sellers
FROM fact_seller;
-- 2. Revenue by Country
-- Output: revenue_by_country.csv

SELECT
    c.country_name,
    SUM(f.sales) AS total_sales
FROM fact_seller f
JOIN dim_country c
    ON f.country_key = c.country_key
GROUP BY c.country_name
ORDER BY total_sales DESC;


-- 3. Revenue by Business Type
-- Output: revenue_by_business.csv

SELECT
    b.business_type,
    SUM(f.sales) AS total_sales
FROM fact_seller f
JOIN dim_business b
    ON f.business_key = b.business_key
GROUP BY b.business_type
ORDER BY total_sales DESC;



-- 4. Top 10 High Risk Sellers
-- Output: high_risk_sellers.csv

SELECT
    f.seller_id,
    r.risk_score
FROM fact_seller f
JOIN dim_risk r
    ON f.risk_key = r.risk_key
ORDER BY r.risk_score DESC
LIMIT 10;


-- 5. Monthly Seller Registrations
-- Output: monthly_registrations.csv

SELECT
    d.year,
    d.month,
    COUNT(*) AS sellers
FROM fact_seller f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- 6. Refund Rate by Business Type
-- Output: refund_rate.csv

SELECT
    b.business_type,
    SUM(f.refunds) AS refunds,
    SUM(f.sales) AS sales,
    ROUND(
        (SUM(f.refunds) * 100.0) / NULLIF(SUM(f.sales), 0),
        2
    ) AS refund_percentage
FROM fact_seller f
JOIN dim_business b
    ON f.business_key = b.business_key
GROUP BY b.business_type
ORDER BY refund_percentage DESC;


-- 7. Average Revenue by Industry
-- Output: industry_revenue.csv

SELECT
    b.industry,
    ROUND(AVG(f.annual_revenue), 2) AS avg_revenue
FROM fact_seller f
JOIN dim_business b
    ON f.business_key = b.business_key
GROUP BY b.industry
ORDER BY avg_revenue DESC;


-- 8. Verification Status
-- Output: verification_status.csv

SELECT
    dv.verification_status,
    COUNT(*) AS seller_count
FROM fact_seller f
JOIN dim_verification dv
    ON f.verification_key = dv.verification_key
GROUP BY dv.verification_status
ORDER BY seller_count DESC;


-- 9. Country Verification Summary
-- Output: country_verification.csv

SELECT
    dc.country_name,
    dv.verification_status,
    COUNT(*) AS seller_count
FROM fact_seller f
JOIN dim_country dc
    ON f.country_key = dc.country_key
JOIN dim_verification dv
    ON f.verification_key = dv.verification_key
GROUP BY
    dc.country_name,
    dv.verification_status
ORDER BY
    dc.country_name,
    seller_count DESC;


-- ============================================
-- DIMENSION TABLE LOADS
-- ============================================


-- 1. Country Dimension
INSERT INTO dim_country

SELECT
    ROW_NUMBER() OVER (
        ORDER BY country
    ) AS country_key,

    country AS country_name

FROM (
    SELECT DISTINCT country
    FROM sellers
);


-- 2. Business Dimension
INSERT INTO dim_business

SELECT
    ROW_NUMBER() OVER (
        ORDER BY business_type, industry
    ) AS business_key,

    business_type,
    industry

FROM (
    SELECT DISTINCT
        business_type,
        industry
    FROM sellers
);


-- 3. Date Dimension
INSERT INTO dim_date

SELECT
    ROW_NUMBER() OVER (
        ORDER BY registration_date
    ) AS date_key,

    registration_date,

    YEAR(registration_date) AS year,
    MONTH(registration_date) AS month,
    DAY(registration_date) AS day

FROM (
    SELECT DISTINCT
        CAST(registration_date AS DATE) AS registration_date
    FROM sellers
);


-- 4. Verification Dimension
INSERT INTO dim_verification

SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            verification_status,
            pan_status,
            gst_status,
            bank_status
    ) AS verification_key,

    verification_status,
    pan_status,
    gst_status,
    bank_status

FROM (
    SELECT DISTINCT
        verification_status,
        pan_status,
        gst_status,
        bank_status
    FROM verification
);


-- 5. Risk Dimension
INSERT INTO dim_risk

SELECT
    ROW_NUMBER() OVER (
        ORDER BY risk_score, fraud_flag
    ) AS risk_key,

    risk_score,
    fraud_flag

FROM (
    SELECT DISTINCT
        risk_score,
        fraud_flag
    FROM fraud
);
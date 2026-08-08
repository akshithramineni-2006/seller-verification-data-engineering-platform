drop table if exists dim_country;
drop table if exists dim_business;
drop table if exists dim_date;
drop table if exists dim_verification;
drop table if exists dim_risk;
drop table if exists fact_seller;


create table dim_country (
   country_key  integer,
   country_name varchar
);


create table dim_business (
   business_key  integer,
   business_type varchar,
   industry      varchar
);


create table dim_date (
   date_key          integer,
   registration_date date,
   year              integer,
   month             integer,
   day               integer
);


create table dim_verification (
   verification_key    integer,
   verification_status varchar,
   pan_status          varchar,
   gst_status          varchar,
   bank_status         varchar
);


create table dim_risk (
   risk_key   integer,
   risk_score integer,
   fraud_flag boolean
);


create table fact_seller (
   seller_id        varchar,
   country_key      integer,
   business_key     integer,
   date_key         integer,
   verification_key integer,
   risk_key         integer,
   annual_revenue   double,
   orders           integer,
   sales            double,
   returns          integer,
   refunds          double
);
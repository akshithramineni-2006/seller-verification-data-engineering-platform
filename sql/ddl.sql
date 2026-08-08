drop table if exists dim_country;
drop table if exists dim_business;
drop table if exists dim_date;
drop table if exists dim_verification;
drop table if exists fact_seller;

create table dim_country (
   country_id   integer,
   country_name varchar
);

create table dim_business (
   business_id   integer,
   business_type varchar,
   industry      varchar
);

create table dim_date (
   date_id           integer,
   registration_date date,
   year              integer,
   month             integer,
   day               integer
);

create table dim_verification (
   verification_id     varchar,
   verification_status varchar,
   pan_status          varchar,
   gst_status          varchar,
   bank_status         varchar
);

create table fact_seller (
   seller_id       varchar,
   country_id      integer,
   business_id     integer,
   date_id         integer,
   verification_id varchar,
   annual_revenue  double,
   orders          integer,
   sales           double,
   returns         integer,
   refunds         double,
   risk_score      integer,
   fraud_flag      boolean
);
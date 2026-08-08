insert into fact_seller
   select s.seller_id,
          c.country_key,
          b.business_key,
          d.date_key,
          v.verification_key,
          r.risk_key,
          s.annual_revenue,
          t.orders,
          t.sales,
          t.returns,
          t.refunds
     from sellers s
     left join transactions t
   on s.seller_id = t.seller_id
     left join verification ver
   on s.seller_id = ver.seller_id
     left join fraud f
   on s.seller_id = f.seller_id
     left join dim_country c
   on s.country = c.country_name
     left join dim_business b
   on s.business_type = b.business_type
      and s.industry = b.industry
     left join dim_date d
   on cast(s.registration_date as date) = d.registration_date
     left join dim_verification v
   on ver.verification_status = v.verification_status
      and ver.pan_status = v.pan_status
      and ver.gst_status = v.gst_status
      and ver.bank_status = v.bank_status
     left join dim_risk r
   on f.risk_score = r.risk_score
      and f.fraud_flag = r.fraud_flag;
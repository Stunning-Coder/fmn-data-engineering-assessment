
  
  create view "warehouse"."main"."stg_monthly_targets__dbt_tmp" as (
    select
    record_id,
    salesperson_id,
    year,
    month,
    region,
    target_revenue_ngn,
    actual_revenue_ngn,
    achievement_pct
from "warehouse"."main"."monthly_targets"
  );

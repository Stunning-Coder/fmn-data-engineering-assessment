
  
  create view "warehouse"."main"."stg_distributors__dbt_tmp" as (
    select
    distributor_id,
    distributor_name,
    region,
    city,
    outlet_type,
    onboarding_date,
    is_active
from "warehouse"."main"."distributors"
  );

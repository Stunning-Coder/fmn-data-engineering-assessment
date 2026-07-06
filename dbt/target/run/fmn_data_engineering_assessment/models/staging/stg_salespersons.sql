
  
  create view "warehouse"."main"."stg_salespersons__dbt_tmp" as (
    select
    salesperson_id,
    salesperson_name,
    region,
    team,
    hire_date,
    monthly_target_ngn
from "warehouse"."main"."salespersons"
  );

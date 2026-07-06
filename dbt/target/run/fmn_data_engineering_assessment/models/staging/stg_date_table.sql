
  
  create view "warehouse"."main"."stg_date_table__dbt_tmp" as (
    select
    date,
    year,
    quarter,
    month,
    month_name,
    week,
    day_of_week,
    is_weekend,
    is_month_end
from "warehouse"."main"."date_table"
  );

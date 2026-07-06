
  
    
    

    create  table
      "warehouse"."main"."mart_sales_performance__dbt_tmp"
  
    as (
      select
    t.transaction_date,
    d.region,
    s.salesperson_name as salesperson,
    t.revenue_ngn as revenue,
    t.gross_profit_ngn as gross_profit,
    t.quantity,
    t.discount_amount_ngn as discount,
    p.product_name as product
from "warehouse"."main"."stg_transactions" as t
left join "warehouse"."main"."stg_products" as p
    on t.product_id = p.product_id
left join "warehouse"."main"."stg_salespersons" as s
    on t.salesperson_id = s.salesperson_id
left join "warehouse"."main"."stg_distributors" as d
    on t.distributor_id = d.distributor_id
left join "warehouse"."main"."stg_date_table" as dt
    on t.transaction_date = dt.date
    );
  
  
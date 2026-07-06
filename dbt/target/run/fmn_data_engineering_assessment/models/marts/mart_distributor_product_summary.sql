
  
    
    

    create  table
      "warehouse"."main"."mart_distributor_product_summary__dbt_tmp"
  
    as (
      select
    d.distributor_name as distributor,
    p.product_name as product,
    d.region,
    sum(t.revenue_ngn) as total_revenue,
    sum(t.quantity) as total_quantity,
    sum(t.gross_profit_ngn) as gross_profit,
    avg(t.discount_amount_ngn) as average_discount,
    count(t.transaction_id) as number_of_transactions
from "warehouse"."main"."stg_transactions" as t
left join "warehouse"."main"."stg_products" as p
    on t.product_id = p.product_id
left join "warehouse"."main"."stg_distributors" as d
    on t.distributor_id = d.distributor_id
group by
    d.distributor_name,
    p.product_name,
    d.region
    );
  
  
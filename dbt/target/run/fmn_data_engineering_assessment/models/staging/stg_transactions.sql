
  
  create view "warehouse"."main"."stg_transactions__dbt_tmp" as (
    select
    transaction_id,
    transaction_date,
    product_id,
    distributor_id,
    salesperson_id,
    quantity,
    unit_price_ngn,
    discount_pct,
    discount_amount_ngn,
    revenue_ngn,
    cogs_ngn,
    gross_profit_ngn,
    payment_method,
    delivery_status,
    transaction_status,
    notes
from "warehouse"."main"."transactions"
  );

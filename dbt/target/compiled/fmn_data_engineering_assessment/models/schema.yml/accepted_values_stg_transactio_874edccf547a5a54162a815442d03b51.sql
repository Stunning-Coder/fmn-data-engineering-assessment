
    
    

with all_values as (

    select
        delivery_status as value_field,
        count(*) as n_records

    from "warehouse"."main"."stg_transactions"
    group by delivery_status

)

select *
from all_values
where value_field not in (
    'delivered','in_transit','pending'
)



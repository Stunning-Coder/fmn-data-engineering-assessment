
    
    

select
    record_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_monthly_targets"
where record_id is not null
group by record_id
having count(*) > 1



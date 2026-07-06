
    
    

select
    date as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_date_table"
where date is not null
group by date
having count(*) > 1



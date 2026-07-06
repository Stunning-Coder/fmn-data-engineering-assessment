
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date
from "warehouse"."main"."stg_date_table"
where date is null



  
  
      
    ) dbt_internal_test
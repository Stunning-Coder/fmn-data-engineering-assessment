
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select record_id
from "warehouse"."main"."stg_monthly_targets"
where record_id is null



  
  
      
    ) dbt_internal_test
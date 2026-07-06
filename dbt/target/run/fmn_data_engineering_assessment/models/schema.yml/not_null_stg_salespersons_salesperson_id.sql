
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select salesperson_id
from "warehouse"."main"."stg_salespersons"
where salesperson_id is null



  
  
      
    ) dbt_internal_test
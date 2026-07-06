select
    salesperson_id,
    salesperson_name,
    region,
    team,
    hire_date,
    monthly_target_ngn
from {{ source('warehouse', 'salespersons') }}

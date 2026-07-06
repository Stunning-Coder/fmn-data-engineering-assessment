select
    date,
    year,
    quarter,
    month,
    month_name,
    week,
    day_of_week,
    is_weekend,
    is_month_end
from {{ source('warehouse', 'date_table') }}

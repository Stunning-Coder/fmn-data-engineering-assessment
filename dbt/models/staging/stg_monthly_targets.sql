select
    record_id,
    salesperson_id,
    year,
    month,
    region,
    target_revenue_ngn,
    actual_revenue_ngn,
    achievement_pct
from {{ source
('warehouse', 'monthly_targets') }}

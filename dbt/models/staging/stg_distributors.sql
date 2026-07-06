select
    distributor_id,
    distributor_name,
    region,
    city,
    outlet_type,
    onboarding_date,
    is_active
from {{ source('warehouse', 'distributors') }}

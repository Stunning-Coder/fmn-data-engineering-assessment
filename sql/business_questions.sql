-- 1. Top 5 products by revenue (2025)
select
    p.product_name,
    round(sum(t.revenue_ngn), 2) as revenue_ngn
from main.transactions as t
join main.products as p on t.product_id = p.product_id
where extract(year from t.transaction_date) = 2025
group by p.product_name
order by revenue_ngn desc
limit 5;

-- 2. Highest MoM growth by region (Q3 2025)
with monthly_region_revenue as (
    select
        d.region,
        extract(month from t.transaction_date) as month_num,
        sum(t.revenue_ngn) as revenue
    from main.transactions as t
    join main.distributors as d on t.distributor_id = d.distributor_id
    where extract(year from t.transaction_date) = 2025
      and extract(quarter from t.transaction_date) = 3
    group by d.region, extract(month from t.transaction_date)
),
region_growth as (
    select
        region,
        month_num,
        revenue,
        lag(revenue) over (partition by region order by month_num) as prev_revenue
    from monthly_region_revenue
)
select
    region,
    month_num,
    revenue,
    round(((revenue - prev_revenue) / nullif(prev_revenue, 0)) * 100, 2) as mom_growth_pct
from region_growth
where prev_revenue is not null
order by mom_growth_pct desc
limit 5;

-- 3. Average target achievement by salesperson
select
    s.salesperson_name,
    round(avg(mt.achievement_pct), 2) as avg_target_achievement_pct
from main.monthly_targets as mt
join main.salespersons as s on mt.salesperson_id = s.salesperson_id
group by s.salesperson_name
order by avg_target_achievement_pct desc;

-- 4. Distributor with highest return rate
select
    d.distributor_name,
    round(
        100.0 * sum(case when t.transaction_status = 'returned' then 1 else 0 end) / nullif(count(*), 0),
        2
    ) as return_rate_pct
from main.transactions as t
join main.distributors as d on t.distributor_id = d.distributor_id
group by d.distributor_name
order by return_rate_pct desc
limit 5;

-- 5. Rolling 3-month revenue trend by category
with monthly_category_revenue as (
    select
        p.category,
        date_trunc('month', t.transaction_date) as month_start,
        sum(t.revenue_ngn) as revenue
    from main.transactions as t
    join main.products as p on t.product_id = p.product_id
    group by p.category, date_trunc('month', t.transaction_date)
)
select
    category,
    month_start,
    revenue,
    avg(revenue) over (
        partition by category
        order by month_start
        rows between 2 preceding and current row
    ) as rolling_3_month_avg_revenue
from monthly_category_revenue
order by category, month_start;

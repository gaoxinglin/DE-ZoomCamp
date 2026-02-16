/* 
Root Cause Analysis - 重复记录的根本原因分析
找出导致重复的具体字段和模式
*/

with int_trips_unioned as (
    select * from {{ ref('int_trips_unioned')}}
),

-- 标记重复记录
duplicate_records as (
    select 
        *,
        count(*) over (
            partition by vendor_id, pickup_datetime, service_type, dropoff_datetime
        ) as duplicate_count
    from int_trips_unioned
    where 1=1
    qualify duplicate_count > 1  -- 只保留重复的记录
),

-- 分析哪些字段在重复记录中不同
field_variation_analysis as (
    select
        -- 分组键
        vendor_id,
        pickup_datetime,
        dropoff_datetime,
        service_type,
        duplicate_count,
        
        -- 统计每个字段的变化情况
        count(distinct pickup_location_id) > 1 as pickup_location_varies,
        count(distinct dropoff_location_id) > 1 as dropoff_location_varies,
        count(distinct trip_distance) > 1 as trip_distance_varies,
        count(distinct fare_amount) > 1 as fare_amount_varies,
        count(distinct total_amount) > 1 as total_amount_varies,
        count(distinct payment_type) > 1 as payment_type_varies,
        count(distinct passenger_count) > 1 as passenger_count_varies,
        count(distinct rate_code_id) > 1 as rate_code_varies,
        
        -- 检查是否存在异常值
        min(fare_amount) < 0 as has_negative_fare,
        min(total_amount) < 0 as has_negative_total,
        min(trip_distance) < 0 as has_negative_distance,
        
        -- 检查是否是瞬时行程（pickup和dropoff时间相同）
        min(pickup_datetime) = min(dropoff_datetime) as is_instant_trip,
        
        -- 显示实际值的范围
        min(fare_amount) as min_fare,
        max(fare_amount) as max_fare,
        min(trip_distance) as min_distance,
        max(trip_distance) as max_distance
        
    from duplicate_records
    group by 
        vendor_id, 
        pickup_datetime, 
        dropoff_datetime, 
        service_type, 
        duplicate_count
)

-- 按问题类型分类
select
    -- 问题分类
    case
        when has_negative_fare or has_negative_total or has_negative_distance then 'NEGATIVE_VALUES'
        when is_instant_trip then 'INSTANT_TRIP'
        when payment_type_varies and fare_amount_varies then 'PAYMENT_AND_FARE_VARY'
        when trip_distance_varies and fare_amount_varies then 'DISTANCE_AND_FARE_VARY'
        when pickup_location_varies or dropoff_location_varies then 'LOCATION_VARIES'
        else 'OTHER'
    end as issue_category,
    
    count(*) as num_duplicate_groups,
    sum(duplicate_count) as total_records_affected,
    avg(duplicate_count) as avg_duplicates_per_group,
    max(duplicate_count) as max_duplicates,
    
    -- 字段变化统计
    sum(case when trip_distance_varies then 1 else 0 end) as groups_with_varying_distance,
    sum(case when fare_amount_varies then 1 else 0 end) as groups_with_varying_fare,
    sum(case when payment_type_varies then 1 else 0 end) as groups_with_varying_payment,
    sum(case when passenger_count_varies then 1 else 0 end) as groups_with_varying_passengers,
    
    -- 异常值统计
    sum(case when has_negative_fare then 1 else 0 end) as groups_with_negative_fare,
    sum(case when is_instant_trip then 1 else 0 end) as groups_with_instant_trip

from field_variation_analysis
group by issue_category
order by total_records_affected desc

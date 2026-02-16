/* 
Duplicate Summary - 重复记录的统计汇总
*/

with int_trips_unioned as (
    select * from {{ ref('int_trips_unioned')}}
),

-- 统计每个组合键的重复次数
trip_counts as (
    select 
        *,
        count(*) over (
            partition by vendor_id, pickup_datetime, service_type, dropoff_datetime
        ) as occurrence_count
    from int_trips_unioned
)

select
    -- 总体统计
    count(*) as total_records,
    count(distinct case when occurrence_count = 1 then concat(vendor_id, pickup_datetime, service_type, dropoff_datetime) end) as unique_trips,
    count(distinct case when occurrence_count > 1 then concat(vendor_id, pickup_datetime, service_type, dropoff_datetime) end) as duplicate_trip_keys,
    sum(case when occurrence_count > 1 then 1 else 0 end) as total_duplicate_records,
    
    -- 重复比例
    round(100.0 * sum(case when occurrence_count > 1 then 1 else 0 end) / count(*), 2) as duplicate_percentage,
    
    -- 重复次数分布
    max(occurrence_count) as max_duplicates_for_single_trip,
    avg(case when occurrence_count > 1 then occurrence_count end) as avg_duplicate_count,
    
    -- 按服务类型统计
    count(distinct case when service_type = 'Yellow' and occurrence_count > 1 then concat(vendor_id, pickup_datetime, service_type, dropoff_datetime) end) as yellow_duplicates,
    count(distinct case when service_type = 'Green' and occurrence_count > 1 then concat(vendor_id, pickup_datetime, service_type, dropoff_datetime) end) as green_duplicates
    
from trip_counts

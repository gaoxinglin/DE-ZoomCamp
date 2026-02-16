/* 
Duplicate Analysis - 分析重复记录的模式和原因
*/

with int_trips_unioned as (
    select * from {{ ref('int_trips_unioned')}}
),

-- 找出重复的组合键
duplicate_keys as (
    select 
        vendor_id,
        pickup_datetime,
        service_type,
        dropoff_datetime,
        count(*) as duplicate_count
    from int_trips_unioned
    group by vendor_id, pickup_datetime, service_type, dropoff_datetime
    having count(*) > 1
),

-- 获取所有重复记录的完整信息
duplicate_records as (
    select 
        t.*,
        dk.duplicate_count
    from int_trips_unioned t
    inner join duplicate_keys dk
        on t.vendor_id = dk.vendor_id
        and t.pickup_datetime = dk.pickup_datetime
        and t.service_type = dk.service_type
        and t.dropoff_datetime = dk.dropoff_datetime
),

-- 分析重复记录在其他字段上的差异
duplicate_field_analysis as (
    select
        vendor_id,
        pickup_datetime,
        service_type,
        dropoff_datetime,
        duplicate_count,
        
        -- 检查各个字段是否在重复记录中有不同值
        count(distinct rate_code_id) as distinct_rate_codes,
        count(distinct pickup_location_id) as distinct_pickup_locations,
        count(distinct dropoff_location_id) as distinct_dropoff_locations,
        count(distinct passenger_count) as distinct_passenger_counts,
        count(distinct trip_distance) as distinct_trip_distances,
        count(distinct trip_type) as distinct_trip_types,
        count(distinct fare_amount) as distinct_fare_amounts,
        count(distinct total_amount) as distinct_total_amounts,
        count(distinct payment_type) as distinct_payment_types,
        
        -- 显示实际的不同值（前3个示例）
        string_agg(distinct cast(trip_distance as string), ', ') as trip_distance_values,
        string_agg(distinct cast(fare_amount as string), ', ') as fare_amount_values,
        string_agg(distinct cast(total_amount as string), ', ') as total_amount_values,
        string_agg(distinct cast(passenger_count as string), ', ') as passenger_count_values
        
    from duplicate_records
    group by vendor_id, pickup_datetime, service_type, dropoff_datetime, duplicate_count
)

-- 最终输出：按重复数量排序
select 
    *,
    -- 判断是否为真正的完全重复
    case 
        when distinct_rate_codes = 1 
            and distinct_pickup_locations = 1
            and distinct_dropoff_locations = 1
            and distinct_passenger_counts = 1
            and distinct_trip_distances = 1
            and distinct_fare_amounts = 1
            and distinct_total_amounts = 1
            and distinct_payment_types = 1
        then 'EXACT_DUPLICATE'  -- 完全相同的记录
        else 'PARTIAL_DUPLICATE'  -- 只有部分字段相同
    end as duplicate_type
from duplicate_field_analysis
order by duplicate_count desc, pickup_datetime

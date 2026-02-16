/* 
Improved fct_trips with better deduplication logic
改进的 fct_trips - 使用更智能的去重逻辑
*/

with int_trips_unioned as (
    select * from {{ ref('int_trips_unioned')}}
),

-- 数据清洗：过滤明显的异常值
cleaned_trips as (
    select *
    from int_trips_unioned
    where 1=1
        -- 过滤负数值（数据质量问题）
        and fare_amount >= 0
        and total_amount >= 0
        and trip_distance >= 0
        -- 过滤瞬时行程（可疑数据）
        and pickup_datetime < dropoff_datetime
        -- 过滤异常距离和费用
        and trip_distance < 1000  -- 防止异常大的距离
        and fare_amount < 10000   -- 防止异常大的费用
),

-- 为重复记录添加排名，选择"最好"的记录
deduplicated as (
    select 
        *,
        row_number() over (
            partition by 
                vendor_id, 
                pickup_datetime, 
                service_type, 
                dropoff_datetime
            order by
                -- 优先选择正常的付款方式（1=信用卡, 2=现金）
                case when payment_type in (1, 2) then 0 else 1 end,
                -- 优先选择更大的金额（通常更完整）
                total_amount desc,
                -- 优先选择更大的距离
                trip_distance desc,
                -- 优先选择有乘客数量的记录
                case when passenger_count > 0 then 0 else 1 end
        ) as row_rank
    from cleaned_trips
),

-- 只保留每组中排名第一的记录
unique_trips as (
    select * except(row_rank)
    from deduplicated
    where row_rank = 1
),

-- 生成最终的 trip_id
fct_trips as (
    select
        md5(cast(concat(
            vendor_id, '_', 
            pickup_datetime, '_', 
            service_type, '_', 
            dropoff_datetime
        ) as string)) as trip_id,
        *
    from unique_trips
)

select * from fct_trips

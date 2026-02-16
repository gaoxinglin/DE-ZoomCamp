with fct_trips as (
    select * 
    from {{ ref('fct_trips') }}
    where fare_amount >= 0 
        and total_amount >= 0
        and trip_distance >= 0
        and pickup_datetime < dropoff_datetime
        and trip_distance < 1000
        and fare_amount < 10000
        and passenger_count between 0 and 6 
),

with duplicate_ids as (
    select trip_id
    from fct_trips
    where pickup_datetime >= '2019-01-01' and pickup_datetime < '2019-01-02'
    group by 1
    having count(*) > 1
)

select
    t.* from fct_trips t
inner join duplicate_ids d on t.trip_id = d.trip_id
where t.pickup_datetime >= '2019-01-01' and t.pickup_datetime < '2019-01-02'
order by t.trip_id;
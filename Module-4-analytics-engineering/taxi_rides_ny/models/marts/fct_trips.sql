/* 
To Do:
- One row per trip （doesn't matter if yellow or green)
- Add a primary key (trip_id). It has to be unique.
- Find all the duplicates. understand why they happen and fix them.
- Find a way to enrich the column payment_type.
*/

with int_trips_unioned as (
    select * from {{ ref('int_trips_unioned')}}
),

fct_trips as (
select
    md5(cast(concat(vendor_id, '_', pickup_datetime, '_', service_type,'_', dropoff_datetime) as string)) as trip_id,
    *
from int_trips_unioned
)

select * from fct_trips

{{ config(materialized='table') }}

with source as (
    select
    id,
    ingested_date,
    home_team,
    away_team,
    game_timestamp,
    replace(game_data::varchar, '"', '') as game_data
    from raw_basket_input
    where game_data::varchar != '"None"'

)

select
id,
(game->>'team')::varchar as team
from source
cross join json_array_elements(game_data::json) game
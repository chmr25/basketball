{{ config(materialized='table') }}

with source as (
    select
    id,
    ingested_date,
    home_team,
    away_team,
    game_timestamp,
    game_data::jsonb
from raw_basket_input
    where game_data::varchar != 'null'
),

game_expanded as (
    select
        *,
        jsonb_array_elements(game_data) as game
    from source
),

adrian_points as (
    select
        id as game_id,
        home_team,
        away_team,
        game_timestamp,
        (game ->> 'score') as score,
        (game ->> 'team') as team_scored,
        (game ->> 'player') as player,
        (game ->> 'basket_count') as basket_count
    from game_expanded
    where game ->> 'player' != 'timeout!'
),

points_scored as (
    select
        game_id,
        game_timestamp,
        home_team,
        away_team,
        count(game_id) filter (where team_scored = 'LagA' and basket_count = '2p') as home_2p,
        count(game_id) filter (where team_scored = 'LagA' and basket_count = '3p') as home_3p,
        count(game_id) filter (where team_scored = 'LagA' and basket_count = '1p') as home_1p,
        count(game_id) filter (where team_scored = 'LagB' and basket_count = '2p') as away_2p,
        count(game_id) filter (where team_scored = 'LagB' and basket_count = '3p') as away_3p,
        count(game_id) filter (where team_scored = 'LagB' and basket_count = '1p') as away_1p
    from adrian_points
    group by 1, 2, 3, 4
)

select * from points_scored
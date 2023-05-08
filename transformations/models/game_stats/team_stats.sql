{{ config(materialized='table') }}

with source as (
    select * from {{ ref("game_stats") }}
),

home_teams as (
    select
        home_team,
        avg(home_2p*2) as home_avg_2p,
        avg(home_1p) as home_avg_1p,
        avg(home_3p*2) as home_avg_3p,
        avg(away_2p*2) as retrieve_avg_2p,
        avg(away_1p) as retrieve_avg_1p,
        avg(away_3p*3) as retrieve_avg_3p
    from source
    group by 1
),

away_teams as (
    select
        away_team,
        avg(away_2p*2) as away_avg_2p,
        avg(away_1p) as away_avg_1p,
        avg(away_3p*2) as away_avg_3p,
        avg(home_2p*2) as retrieve_avg_2p,
        avg(home_1p) as retrieve_avg_1p,
        avg(home_3p*3) as retrieve_avg_3p
    from source
    group by 1
),

final as (
    select
        home_teams.home_team as "name",
        (home_teams.home_avg_1p + away_teams.away_avg_1p)/2 as avg_1p_scored,
        (home_teams.home_avg_2p + away_teams.away_avg_2p)/2 as avg_2p_scored,
        (home_teams.home_avg_3p + away_teams.away_avg_3p)/2 as avg_3p_scored,
        (home_teams.retrieve_avg_1p + away_teams.retrieve_avg_1p)/2 as avg_1p_retrieved,
        (home_teams.retrieve_avg_2p + away_teams.retrieve_avg_2p)/2 as avg_2p_retrieved,
        (home_teams.retrieve_avg_3p + away_teams.retrieve_avg_3p)/2 as avg_3p_retrieved
    from home_teams
    left join away_teams on home_teams.home_team = away_teams.away_team
)

select * from final
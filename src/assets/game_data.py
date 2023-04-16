import fitz
import uuid
from dagster import asset, get_dagster_logger, AssetIn
from datetime import datetime
from src.io_manager.postgres_io_manager import RawBasketInput
import os
import json

logger = get_dagster_logger()


def get_words_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    words = doc[0].get_text("words")
    actual_words = []
    for i in words:
        actual_words.append(i[4])
    return actual_words


def get_period_data(words: list, period: int):
    start = None
    stop = None
    for index, word in enumerate(words):
        if (
            word == "Start"
            and words[index + 1] == "period"
            and words[index + 2] == str(period)
        ):
            start = index + 3
        if period != 4:
            if word == "Start" and words[index + 2] == str(period + 1):
                stop = index
                break
        else:
            if word == "Scores" or (word == "Start" and words[index + 1] == "OT"):
                stop = index
                break
    period_data = words[start:stop]
    return period_data


def get_ot_data(words: list):
    start = None
    stop = None
    ot_data = []
    ot = 0
    for index, word in enumerate(words):
        if word == "Start" and words[index + 1] == "OT":
            start = index + 3
            print("This is the start")
            print(start)
            ot += 1
        if (
            word == "Start"
            and words[index + 1] == "OT"
            and words[index + 2] == str(ot + 1)
        ):
            stop = index
            break
        else:
            if word == "Scores":
                stop = index
                break
    print(f"start is {start} and stop is {stop} ")
    if start and stop:
        print("woohoo")
        ot_data = words[start:stop]
    return ot_data


def contains(larger, smaller):
    larger_iter = iter(larger)
    return all(s in larger_iter for s in smaller)


def clean_period_data(actual_words: list):
    period_data = []
    ot_data = []
    timeouts = []
    empty = [
        "Final",
        "score",
        "0",
        "-",
        "0",
    ]
    if contains(actual_words, empty):
        return
    for period in range(1, 5):
        period_data += get_period_data(words=actual_words, period=period)
    ot_data = get_ot_data(words=actual_words)
    game_data = period_data + ot_data
    timeouts = [
        index - 2 for index, element in enumerate(game_data) if element == "timeout"
    ]
    print(f"Timeouts: {timeouts}")
    count = 0
    for i in range(len(timeouts)):
        game_data.insert(timeouts[i] + count, "timeout!")
        count += 1
    print(f"The count is : {count}")
    period_rows = []
    for i in range(0, len(game_data), 7):
        print(i)
        period_rows.append(
            {
                'score': game_data[i] + game_data[i + 1] + game_data[i + 2],
                'player': game_data[i + 3],
                'team': game_data[i + 4] + "" + game_data[i + 5],
                'basket_count': game_data[i + 6],
            }
        )
    return period_rows


def get_team_names(words):
    for index, word in enumerate(words):
        if word == "Hemmalag:":
            start_hem = index + 1
        elif word == "Bortalag:":
            stop_hem = index
            start_bort = index + 1
        elif word == "Competition:":
            stop_bort = index
            break
    return {
        "hem": " ".join(str(w) for w in words[start_hem:stop_hem]),
        "bort": " ".join(str(w) for w in words[start_bort:stop_bort]),
    }

def get_game_timestamp(words):
    format = "%Y-%m-%d %H:%M"
    for index,word in enumerate(words):
        if word == 'Date' and words[index+1] == '&' and words[index+2]=='time:':
            date_time = words[index+3] + ' ' + words[index+4]
    return datetime.strptime(date_time, format)

def get_game_score(words):
    for index,word in enumerate(words):
        if word == "Final" and words[index+1] == "score" and words[index+5] == "Sekreterare":
            game_score = words[index+2] + "-" + words[index+4]
    return game_score

def create_game_entry(periods, teams, protocol, game_timestamp, game_score):
    logger.info(protocol.split("/")[-1])
    return RawBasketInput(
        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, protocol.split("/")[-1])),
        ingested_date=datetime.today(),
        home_team=teams["hem"],
        away_team=teams["bort"],
        game_timestamp=game_timestamp,
        game_score=game_score,
        game_data=periods,
    )


@asset(
    ins={"files": AssetIn("download_pdfs")},
    required_resource_keys={"local_folder"},
    group_name="game_stats",
    io_manager_def="postgres_io_manager",
)
def get_game_data(files):
    logger.info(f"Data of {len(files)} games will be added")
    match = []
    for pdf in files:
        actual_words = get_words_from_pdf(pdf)
        periods = clean_period_data(actual_words)
        teams = get_team_names(actual_words)
        game_timestamp = get_game_timestamp(actual_words)
        game_score = get_game_score(actual_words)
        match.append(create_game_entry(periods=periods, teams=teams, protocol=pdf, game_timestamp=game_timestamp, game_score=game_score))
    return match
    
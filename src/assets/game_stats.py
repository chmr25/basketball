import fitz
import pandas as pd


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
    count = 0
    for i in range(len(timeouts)):
        game_data.insert(timeouts[i] + count, "timeout!")
        count += 1
    period_rows = []
    for i in range(0, len(game_data), 7):
        period_rows.append(
            {
                "score": game_data[i] + game_data[i + 1] + game_data[i + 2],
                "player": game_data[i + 3],
                "team": game_data[i + 4] + "" + game_data[i + 5],
                "basket_count": game_data[i + 6],
            }
        )
    return pd.DataFrame(period_rows)

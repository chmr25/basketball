import fitz
import pandas as pd

def get_words_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    words = doc[0].get_text("words")
    actual_words = []
    for i in words:
        actual_words.append(i[4])
    return actual_words

def hemmalag_words(words):
    start = None
    stop = None
    count_bortalag = 0
    for index, word in enumerate(words):
        if  word == "OT:":
            start = index+2 
        if word == "Bortalag:":
            count_bortalag += 1
            stop = index
            if count_bortalag == 2:
                break
    hem = words[start:stop]
    return hem

def bortalag_words(words):
    start = None
    stop = None
    for index, word in enumerate(words):
        if  word == "OT:":
            start = index+2 
        if word == "Actions":
            stop = index
            break
    bort = words[start:stop]
    return bort

def get_first_row(lag):
    lag = lag[5:]
    points = None
    first_row = None
    for index,value in enumerate(lag):
        if value.isnumeric() and lag[index+2].isnumeric():
            points = index
            first_row = {
                "player_name": " ".join(lag[1:index]),
                "points": lag[index],
                "fouls": lag[index+1]
            }
            break
    return first_row

def clear_players_table(t_team):
    indexes = []
    player_rows = [get_first_row(t_team)]
    for index, value in enumerate(t_team):
        if value.isnumeric() and index+2<len(t_team) and t_team[index+2].isnumeric() and t_team[index+2] != 'C':
            indexes.append(index+3)
    for i,d in enumerate(indexes):
        player_rows.append(
            {
                "player_name": " ".join(t_team[d:indexes[i+1]-3]) if i+1<len(indexes) else " ".join(t_team[d:d+2]),
                "points": t_team[indexes[i+1]-3] if i+1<len(indexes) else t_team[d+2],
                "fouls": t_team[indexes[i+1]-2] if i+1<len(indexes) else t_team[d+3]
            }
        )
    return player_rows

def csv_lag(lag):    
    rows = []
    ny_lag = [x for x in lag if x not in ['X', 'Ø']]
    player_stats = clear_players_table(ny_lag)
    lag_df = pd.DataFrame(player_stats)
    return lag_df

def get_period_data(words: list, period: int):
    start = None
    stop = None
    for index, word in enumerate(words):
        if  word == "Start" and words[index+1] == 'period' and words[index+2]== str(period):
            start = index+3
        if period != 4:
            if word == "Start" and words[index+2]== str(period+1):
                stop = index
                break
        else:
            if word == "Scores" or (word == "Start" and words[index+1] == 'OT'):
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
        if  word == "Start" and words[index+1] == 'OT':
            start = index+3
            print("This is the start")
            print(start)
            ot += 1
        if word == "Start" and words[index+1] == 'OT' and words[index+2]== str(ot+1):
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
    empty = ['Final', 'score', '0', '-', '0',]
    if contains(actual_words, empty):
        return
    for period in range(1,5):
        period_data += get_period_data(words=actual_words, period=period)
    ot_data = get_ot_data(words=actual_words)
    game_data = period_data + ot_data
    timeouts = [index-2 for index,element in enumerate(game_data) if element == 'timeout']
    count=0
    for i in range(len(timeouts)):
        game_data.insert(timeouts[i]+count, "timeout!")
        count += 1
    period_rows = []
    for i in range(0,len(game_data),7):
        period_rows.append(
            {
                "score": game_data[i] + game_data[i+1] + game_data[i+2],
                "player": game_data[i+3],
                "team":  game_data[i+4] + '' + game_data[i+5],
                "basket_count": game_data[i+6]
            }
        )
    return pd.DataFrame(period_rows)

def main():
    actual_words = get_words_from_pdf('protocols/31325186.pdf')
    print(actual_words)
    match = clean_period_data(actual_words)
    print(match)
    # print(f"The pdf looks like: \n {bortalag_csv} \n {match}")

if __name__ == '__main__':
    main()
from urllib.request import Request, urlopen
import requests
import re, os


def code_of_site(url):
    source_code = open("prefixio_page.txt", "w")
    hdr = {
        "user-agent": "Mozilla/5.0 "
        "(Linux; Android 6.0; "
        "Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/92.0.4515.107 Mobile Safari/537.36"
    }
    source_code.write(str(urlopen(Request(url, headers=hdr)).read()))


def find_games(filename):
    with open(filename, "r") as file:
        html_code = file.read()
    outcome = re.findall(
        r"Match: [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]</div>", str(html_code)
    )
    game_codes = [x.replace("Match: ", "").replace("</div>", "") for x in outcome]
    return game_codes


def get_protocols(game):
    url = "https://www.profixio.com/app/leagueid13825/match/"
    match = game
    protocol = "/protocol/pdf"
    response = requests.get(url + match + protocol)
    with open(f"protocols/{match}.pdf", "wb") as f:
        f.write(response.content)

def check_if_protocols_exist(protocols):
    path = os.path.abspath(os.getcwd())
    folder = '/protocols/'
    missing = [x for x in protocols if not os.path.exists(path + folder + x + '.pdf')]
    return missing

def main():
    url = (
        "https://www.profixio.com/app/leagueid13825/category/1128802?segment=historikk"
    )
    code_of_site(url)
    list_of_games = find_games("prefixio_page.txt")
    games = check_if_protocols_exist(list_of_games)
    for game in games:
        get_protocols(game=game)


if __name__ == "__main__":
    main()

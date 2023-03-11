from urllib.request import Request, urlopen
from dagster import asset, get_dagster_logger, define_asset_job, AssetSelection
# from src.io_manager.file_io_manager import pdf_io_manager
import requests
import re, os

logger = get_dagster_logger()

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


def get_protocols(match):
    url = "https://www.profixio.com/app/leagueid13825/match/"
    protocol = "/protocol/pdf"
    response = requests.get(url + match + protocol)
    path = f"protocols/{match}.pdf"
    return response.content

def check_if_protocols_exist(protocols):
    path = os.path.abspath(os.getcwd())
    folder = '/protocols/'
    missing = [x for x in protocols if not os.path.exists(path + folder + x + '.pdf')]
    return missing

# @asset(io_manager_def=pdf_io_manager)
# def fetch_protocol():
#     url = (
#         "https://www.profixio.com/app/leagueid13825/category/1128802?segment=historikk"
#     )
#     code_of_site(url)
#     list_of_games = find_games("prefixio_page.txt")
#     logger.info(list_of_games)
#     games = check_if_protocols_exist(list_of_games)
#     logger.info(games)
#     return get_protocols(game=games[0])
# 
# fetch_protocols_job = define_asset_job(
#     "fetch_match_protocols",
#     selection=AssetSelection.assets(fetch_protocol),
# )

@asset
def return_a_list():
    return [{'a': 1, 'b':4}]

return_a_list_job = define_asset_job(
    name='example_job',
    selection=AssetSelection.assets(return_a_list)
)



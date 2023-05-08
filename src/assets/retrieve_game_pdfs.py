from urllib.request import Request, urlopen
from dagster import asset, get_dagster_logger
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


def get_protocols(matches):
    url = "https://www.profixio.com/app/leagueid13825/match/"
    protocol = "/protocol/pdf"
    pdfs = []
    for i in matches:
        response = requests.get(url + i + protocol)
        file_name = f"{i}.pdf"
        pdfs.append({"bytes": [response.content], "file_name": file_name})
    return pdfs


@asset(required_resource_keys={"local_folder"}, group_name="collect_data", name="download_pdfs")
def fetch_protocol(context):
    urls = [
        "https://www.profixio.com/app/leagueid13825/category/1128802?segment=historikk",
        "https://www.profixio.com/app/leagueid13825/category/1133937?segment=historikk"
    ]
    profixio_pdfs = []
    for url in urls:
        code_of_site(url)
        list_of_games = find_games("prefixio_page.txt")
        file_obj = context.resources.local_folder
        pdfs_to_add = file_obj.check_if_protocol_exists(list_of_games)
        logger.info(f"{len(pdfs_to_add)} will be added")
        pdfs = get_protocols(matches=pdfs_to_add)
        file_obj.write_to_path(pdfs=pdfs)
        pdfs_total = [
            context.resources.local_folder.target_path + '/' + pdf + '.pdf'
            for pdf in pdfs_to_add
        ]
        profixio_pdfs.extend(pdfs_total)
    return profixio_pdfs

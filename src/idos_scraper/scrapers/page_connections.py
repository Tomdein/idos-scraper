import requests
from bs4 import BeautifulSoup
import re
import json

from .. import log
from .search_connections import ParseConnectionsDetails

# create logger
logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)
logger.addHandler(log.ch)


def PageConnections(ids_list: list, handle: int, arrivalThere: str, searchDate: str) -> dict | None:
    url = "https://idos.idnes.cz/odis/Ajax/ConnPaging"

    querystring = {"callback": "wheee"}

    connId = ids_list[-1]
    payload = [("listedIds[]", f"{ids}") for ids in ids_list]
    payload.extend([("isPrev", "false"),
                    ("arrivalThere", f"{arrivalThere}"),
                    ("handle", f"{handle}"),
                    ("searchDate", f"{searchDate}"),
                    ("connId", f"{connId}")
                    ])

    response = requests.request("POST", url, data=payload, params=querystring)

    re_html_match = re.compile("^wheee\((\{.*\})\);$").search(response.text)
    if re_html_match is None:
        logger.critical("Error extracting HTML from jQuery response while paging more connections")
        raise Exception("Error extracting HTML from jQuery response while paging more connections")


    response_json = json.loads(re_html_match.group(1).replace("\\r\\n",""))

    # Extract key "newConnections" from parsed json for use in _ParseConnResult
    response_html_json = {"newConnections": response_json["newConnections"]}
    response_json.pop("newConnections")

    keys = ["connData", "legend"]
    pruned_connResult = {key: response_json[key] for key in keys}

    connections_query = dict()
    connections_query["connResult"] = pruned_connResult
    connections_query["connections"] = list()

    for connection in response_html_json["newConnections"]:
        soup = BeautifulSoup(connection, 'html.parser')
        # Adds connection to connections_query["connections"]
        connections_query["connections"].append(ParseConnectionsDetails(soup)["connections"][0])

    logger.debug(connections_query["connections"])

    return connections_query

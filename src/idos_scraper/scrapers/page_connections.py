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

def _GetQueryPaging(ids_list: list, handle: int, arrivalThere: str, searchDate: str) -> dict:
    paging_query = dict()
    paging_query["url"] = "https://idos.idnes.cz/odis/Ajax/ConnPaging"

    paging_query["querystring"] = {"callback": "wheee"}

    connId = ids_list[-1]
    paging_query["payload"] = [("listedIds[]", f"{ids}") for ids in ids_list]
    paging_query["payload"].extend([("isPrev", "false"),
                    ("arrivalThere", f"{arrivalThere}"),
                    ("handle", f"{handle}"),
                    ("searchDate", f"{searchDate}"),
                    ("connId", f"{connId}")
                    ])
    
    return paging_query

def _ParsePagingResponse(response_text) -> dict:
    re_html_match = re.compile("^wheee\((\{.*\})\);$").search(response_text)
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

def PageConnections(ids_list: list, handle: int, arrivalThere: str, searchDate: str) -> dict | None:
    paging_query = _GetQueryPaging(ids_list, handle, arrivalThere, searchDate)

    response = requests.request("POST", paging_query["url"], data=paging_query["payload"], params=paging_query["querystring"])

    return _ParsePagingResponse(response.text)

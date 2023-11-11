import requests
from bs4 import BeautifulSoup
import re
import json

from .. import log

# create logger
logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)
logger.addHandler(log.ch)


def SearchConnectionsByStation(station_from: str = "Horni polanka", station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
    querystring = {"f":f"{station_from}","t":f"{station_to}"}
    
    if time is not None:
        querystring["time"] = time

    if date is not None:
        querystring["date"] = date

    return SearchConnections(querystring)

# The same as GetConnectionsByStation, but the station_from can be empty and will be autofilled with your coordinates
# Uses "fc" query parameter! And "f" is "Moje poloha"
def SearchConnectionsByLocation(station_from: str | None = None, station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
    logger.warning(f"SearchConnectionsByLocation is not yet fully implemented")
    querystring = {"f":"Moje poloha","t":f"{station_to}"}
        
    if time is not None:
        querystring["time"] = time

    if date is not None:
        querystring["date"] = date

    if station_from is None:
        station_from = "loc:49.8384522; 18.1538506%myPosition=true"

    querystring["fc"] = station_from
    
    return SearchConnections(querystring)

def SearchConnections(querystring: dict) -> dict:
    url = "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/vysledky/"

    # does not work querystring = {"date":"4.11.2023","time":"02:01", "fs":"1", "f":"loc:49,788988@18,169573","t":"VŠB-TUO"}
    # does not work querystring = {"date":"4.11.2023","time":"02:01", "fs":"1", "f":"loc:49°11'28.4\"N@16°36'44.61\"E","t":"VŠB-TUO"}
    # querystring = {"date":"4.11.2023","time":"02:01","f":"H Pola","t":"VŠB-TUO"}
    # querystring = {"f":"VŠB-TUO","t":"Horni polanka"}
    # querystring = {"date":"4.11.2023","time":"13:15", "f":"Moje poloha", "fc":"loc:49.8384522; 18.1538506%myPosition=true","t":"VŠB-TUO"}

    response = requests.request("GET", url, params=querystring)

    return ParseConnections(response)

def SearchConnectionsPOST() -> dict:
    url = "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/"
    #url = "https://idos.idnes.cz/odis/spojeni/"

    payload = {
        "From": "Horni Polanka",    # "Moje poloha"
        "FromHidden": "",           # "loc:48.789;14.1696%myPosition=true"
        "positionACPosition": "",
        "To": "VSB-TUO",
        "ToHidden": "Horni Polanka%303003",
        "positionACPosition": "",
        "AdvancedForm.Via[0]": "",
        "AdvancedForm.ViaHidden[0]": "",
        "Date": "",
        "Time": "",
        "IsArr": "False",
    }

    response = requests.request("POST", url, data=payload)

    return ParseConnections(response)

def ParseConnections(response: requests.Response) -> dict:
    soup = BeautifulSoup(response.text, 'html.parser')

    conn_result = ParseConnResult(soup)

    connections_query = dict()
    connections_query["connResult"] = conn_result

    # Adds connections_query["connections"]
    connections_query.update(ParseConnectionsDetails(soup))

    logger.debug(connections_query["connections"])

    return connections_query

def ParseConnResult(soup: BeautifulSoup) -> dict | None:
    connection_result_js = soup.find_all("script", type="text/javascript", string=re.compile("^var params = new Conn\.ConnFormParams"))

    if len(connection_result_js) == 0:
        return None

    result_js = connection_result_js[0].contents[0]

    re_connResult_match = re.compile("var connResult = new Conn\.ConnResult\(params, null, (\{.*?\})\);").search(result_js)
    if re_connResult_match is None:
        return None

    #connResult = chompjs.parse_js_object(re_connResult_match.group(1))
    connResult = json.loads(re_connResult_match.group(1))

    keys = ["handle", "connData", "searchItem", "legend", "absCombId", "arrivalThere"]
    pruned_connResult = {key: connResult[key] for key in keys}
    pruned_connResult["searchDate"] = pruned_connResult["searchItem"]["oConn"]["oUserInput"]["dtSearchDate"]

    # ?: connResult might have interesting data left

    return pruned_connResult

def ParseConnectionsDetails(soup: BeautifulSoup) -> dict:
    connection_query = dict()
    connection_query["connections"] = list()

    connection_details = soup.find_all("div", class_="connection-details")

    # Scraping single connection with possibly more than 2 transfers (non direct connections)
    for html_connection in connection_details:
        logger.debug(f"Connection:")
        html_single_connections = html_connection.find_all("div", class_="outside-of-popup")

        conn = dict()
        conn["single_connections"] = list()

        # Fill ID of connection
        re_id_match = re.compile("^connectionBox-(\d*)$").match(html_connection.parent["id"])
        if re_id_match is None:
            logger.critical("Unable to find connection ID in html <div>'s 'id' attribute")
            raise Exception("Unable to find connection ID in html <div>'s 'id' attribute")

        conn["id"] = re_id_match.group(1)

        for html_single in html_single_connections:
            conn_single = {}

            # Fill delay
            conn_single["delay"] = ParseDelay(html_single)

            # Fill icon
            conn_single["icon"] = ParseIcon(html_single)

            # Fill connection type and number
            # conn_single["type"] = ""
            # conn_single["number"] = ""
            conn_single.update(ParseTypeAndNumber(html_single))
            logger.debug(f"\tA {conn_single['type']} {conn_single['number']}:")

            # Fill stations and departure/arrival times
            # conn_single["times"] = list()
            # conn_single["stations"] = list()
            # conn_single["platforms"] = list()
            conn_single.update(ParseSingleConnectionDetail(html_single))
            logger.debug(
                f"\t\tDeparture at {conn_single['times'][0]} from {conn_single['stations'][0]}."
                f" Arrival at {conn_single['times'][1]} at {conn_single['stations'][1]}."
                )

            conn["single_connections"].append(conn_single)

        connection_query["connections"].append(conn)

    return connection_query

def ParseDelay(html_single) -> str | None:
    conn_delay = html_single.find("span", class_=re.compile("^conn-result-delay-bubble-"))

    if len(conn_delay.contents) != 3 or conn_delay.contents[1].text is None:
        return None

    return conn_delay.contents[1].text.replace("\\r\\n", "").rstrip()

def ParseIcon(html_single) -> str | None:
    html_connection_string_container = html_single.find("div", class_="title-container")

    connection_icon_path = html_connection_string_container.find("img")["src"]
    re_match_icon = re.compile("/images/trtype/(2.svg|3.svg)").search(connection_icon_path)

    if re_match_icon is None:
        return None

    return re_match_icon.group(1)

def ParseTypeAndNumber(html_single) -> dict:
    html_connection_string_container = html_single.find("div", class_="title-container")
    connection_num = html_single.find("h3").contents[0].contents[0]

    connection_string = html_connection_string_container.find("h3").contents[0].contents[0]

    conn_single = dict()
    conn_single["type"] = None
    conn_single["number"] = None

    re_match = re.compile("(Bus|Tram) (\d*)").search(connection_string)
    if re_match is not None:
        conn_single["type"] = re_match.group(1)
        conn_single["number"] = re_match.group(2)

    return conn_single

def ParseSingleConnectionDetail(html_single):
    station_times = html_single.find_all("li", class_="item")

    conn_single = dict()
    conn_single["times"] = list()
    conn_single["stations"] = list()
    conn_single["platforms"] = list()

    for station_and_time in station_times:
        conn_single["times"].append(station_and_time.find("p", class_="time").next_element)
        conn_single["stations"].append(station_and_time.find("p", class_="station").next_element.next_element)
        conn_single["platforms"].append(station_and_time.find("span", title=["nástupiště","stanoviště"]).contents[0])

    return conn_single
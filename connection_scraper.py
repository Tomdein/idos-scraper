import requests
from bs4 import BeautifulSoup
import re
import logging

# -------------------- Setting up logging --------------------
# https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# https://chrisyeh96.github.io/2020/03/28/terminal-colors.html
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    #format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = " %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: green + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
# create logger with 'spam_application'
logger = logging.getLogger("Scrapper")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

# logger.debug("debug message")
# logger.info("info message")
# logger.warning("warning message")
# logger.error("error message")
# logger.critical("critical message")
# -------------------- Setting up logging --------------------

def GetConnectionsByStation(station_from: str = "Horni polanka", station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
    querystring = {"f":f"{station_from}","t":f"{station_to}"}
    
    if time is not None:
        querystring["time"] = time

    if date is not None:
        querystring["date"] = date

    return GetConnections(querystring)

# The same as GetConnectionsByStation, but the station_from can be empty and will be autofilled with your coordinates
# Uses "fc" query parameter! And "f" is "Moje poloha"
def GetConnectionsByLocation(station_from: str | None = None, station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
    querystring = {"f":"Moje poloha","t":f"{station_to}"}
        
    if time is not None:
        querystring["time"] = time

    if date is not None:
        querystring["date"] = date

    if station_from is None:
        station_from = "loc:49.8384522; 18.1538506%myPosition=true"

    querystring["fc"] = station_from
    
    return GetConnections(querystring)

def GetConnections(querystring: dict) -> dict:
    url = "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/vysledky/"

    # does not work querystring = {"date":"4.11.2023","time":"02:01", "fs":"1", "f":"loc:49,788988@18,169573","t":"VŠB-TUO"}
    # does not work querystring = {"date":"4.11.2023","time":"02:01", "fs":"1", "f":"loc:49°11'28.4\"N@16°36'44.61\"E","t":"VŠB-TUO"}
    # querystring = {"date":"4.11.2023","time":"02:01","f":"H Pola","t":"VŠB-TUO"}
    # querystring = {"f":"VŠB-TUO","t":"Horni polanka"}
    # querystring = {"date":"4.11.2023","time":"13:15", "f":"Moje poloha", "fc":"loc:49.8384522; 18.1538506%myPosition=true","t":"VŠB-TUO"}

    payload = ""
    headers = {"cookie": "Idos4=DId%3DWoEEDlGBVeGFMevBT9Ryt7Z%2BQuha2YZXKUjo7EMcNsnzlt5QwiYQgQ%3D%3D%26LS%3DZIQdlw6zEyldp5HNOVvWlyOzt2oW97mnHN%2FnMWnLmfprxYUKlsKllfKSi8wkExpXEd55KhWsLKOLxCBCrPb3Eg%3D%3D"}

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    soup = BeautifulSoup(response.text, 'html.parser')
    connection_details = soup.find_all("div", class_="connection-details")

    connections_list = list()

    for connection in connection_details:
        logger.debug(f"Connection:")
        single_connections = connection.find_all("div", class_="outside-of-popup")

        conn = list()

        for single in single_connections:
            conn_single = {}

            # Fill delay
            conn_delay = single.find("span", class_=re.compile("^conn-result-delay-bubble-"))
            conn_single["delay"] = None
            if(len(conn_delay.contents) == 3):
                conn_single["delay"] = conn_delay.contents[1].string

            # Fill icon
            # connection_num = single.find("h3").next_element.next_element
            connection_string_container = single.find("div", class_="title-container")
            connection_icon_path = connection_string_container.find("img")["src"]
            re_match_icon = re.compile("/images/trtype/(2.svg|3.svg)").search(connection_icon_path)
            conn_single["icon"] = None
            if re_match_icon is not None:
                conn_single["icon"] = re_match_icon.group(1)
                

            # Fill connection type and nnumber
            connection_num = single.find("h3").contents[0].contents[0]
            connection_string = connection_string_container.find("h3").contents[0].contents[0]
            conn_single["type"] = None
            conn_single["number"] = None

            re_match = re.compile("(Bus|Tram) (\d*)").search(connection_string)
            if re_match is not None:
                conn_single["type"] = re_match.group(1)
                conn_single["number"] = re_match.group(2)

            logger.debug(f"\tA {re_match.group(1)} {re_match.group(2)}:")

            # Fill stations and departure/arrival times
            station_times = single.find_all("li", class_="item")
            
            conn_single["times"] = list()
            conn_single["stations"] = list()

            for station_and_time in station_times:
                conn_single["times"].append(station_and_time.find("p", class_="time").next_element)
                conn_single["stations"].append(station_and_time.find("p", class_="station").next_element.next_element)

            logger.debug(
                f"\t\tDeparture at {conn_single['times'][0]} from {conn_single['stations'][0]}."
                f" Arrival at {conn_single['times'][1]} at {conn_single['stations'][1]}."
                )

            conn.append(conn_single)

        connections_list.append(conn)

    logger.debug(connections_list)

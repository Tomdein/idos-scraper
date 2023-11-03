import requests
from bs4 import BeautifulSoup

url = "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/vysledky/"

# does not work querystring = {"date":"4.11.2023","time":"02:01", "fs":"1", "f":"loc:49,788988@18,169573","t":"VŠB-TUO"}
# does not work querystring = {"date":"4.11.2023","time":"02:01", "fs":"1", "f":"loc:49°11'28.4\"N@16°36'44.61\"E","t":"VŠB-TUO"}
querystring = {"date":"4.11.2023","time":"02:01","f":"H Pola","t":"VŠB-TUO"}
querystring = {"date":"4.11.2023","time":"02:01", "f":"Moje poloha", "fc":"loc:49.8384522; 18.1538506%myPosition=true","t":"VŠB-TUO"}

payload = ""
headers = {"cookie": "Idos4=DId%3DWoEEDlGBVeGFMevBT9Ryt7Z%2BQuha2YZXKUjo7EMcNsnzlt5QwiYQgQ%3D%3D%26LS%3DZIQdlw6zEyldp5HNOVvWlyOzt2oW97mnHN%2FnMWnLmfprxYUKlsKllfKSi8wkExpXEd55KhWsLKOLxCBCrPb3Eg%3D%3D"}

response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
soup = BeautifulSoup(response.text, 'html.parser')
connection_details = soup.find_all("div", class_="connection-details")

for connection in connection_details:
    print(f"Connection:")
    single_connections = connection.find_all("div", class_="outside-of-popup")

    for single in single_connections:
        connection_num = single.find("h3").next_element.next_element
        print(f"\tA bus/tram {connection_num}:")

        station_times = single.find_all("li", class_="item")

        time = list()
        station = list()
        for station_and_time in station_times:
            time.append(station_and_time.find("p", class_="time").next_element)
            station.append(station_and_time.find("p", class_="station").next_element.next_element)

        print(f"\t\tDeparture at {time[0]} from {station[0]}. Arrival at {time[1]} at {station[1]}.")
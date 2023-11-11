# IDOS scraper

This package scrapes data from Czech public transport provided on page [idos.idnes.cz](https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/).

You can search connections, page more connections (uses web contex from search connections and ajax queries) or search stations by name or location.
For more info, go take a look at sources in idos_scraper.scrapers:
- search_connections.py - Search connections
  - Searches only from ../vlakyautobusymhdvse/..
- page_connections.py - Page connections
- search_station.py - Finding stations
    - For now the station scraper scrapes from ../ostrava/.. url - Only stations in Ostrava city

More filtes (PID, ODIS, IDOL, ...) are comming later.

## TLDR
You will mainly use these 2 functions:
```python
def SearchConnectionsByStation(station_from: str = "Horni polanka", station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
```

```python
def SearchStation(station_short_str: str, number_of_hints_to_query: str | int = 3):
```

And their `async` variants:
```python
async def async_SearchConnectionsByStation(station_from: str = "Horni polanka", station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
```

```python
async def async_SearchStation(station_short_str: str, number_of_hints_to_query: str | int = 3):
```

Not yet fully implemented:
```python
def SearchConnectionsByLocation(station_from: str | None = None, station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
```

```python
def async_SearchConnectionsByLocation(station_from: str | None = None, station_to: str = "VŠB-TUO", time: str | None = None, date: str | None = None) -> dict:
```

## Examples
For examples how to use this module, run:

```bash
python3 -m idos_scraper.examples.ui_search_station
```
or

```bash
python3 -m idos_scraper.examples.search_and_page_connection
```
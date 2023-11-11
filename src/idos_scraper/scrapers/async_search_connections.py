import aiohttp
import urllib.parse

from .. import log
from .search_connections import _GetQuerystringByStation, _GetQuerystringByLocation, ParseConnections

# create logger
logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)
logger.addHandler(log.ch)

# SearchConnectionsByStation & SearchConnectionsByLocation call SearchConnections
# async_SearchConnectionsByStation & async_SearchConnectionsByLocation call async_SearchConnections
# Both SearchConnections and async_SearchConnections use blocking ParseConnections

async def async_SearchConnectionsByStation(station_from: str = "Horni polanka",
                                           station_to: str = "VŠB-TUO",
                                           time: str | None = None,
                                           date: str | None = None,
                                           session: aiohttp.ClientSession | None = None
                                           ) -> dict:
    querystring = _GetQuerystringByStation(station_from, station_to, time, date)

    return await async_SearchConnections(querystring)

async def async_SearchConnectionsByLocation(station_from: str | None = None,
                                            station_to: str = "VŠB-TUO",
                                            time: str | None = None,
                                            date: str | None = None,
                                            session: aiohttp.ClientSession | None = None
                                            ) -> dict:
    logger.warning(f"SearchConnectionsByLocation is not yet fully implemented")
    querystring = _GetQuerystringByLocation(station_from, station_to, time, date)
    
    return await async_SearchConnections(querystring)

async def async_SearchConnections(querystring: dict,
                                  session: aiohttp.ClientSession | None = None
                                  ) -> dict:
    url = "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/vysledky/" + "?" + urllib.parse.urlencode(querystring, doseq=False)

    logger.debug(url)

    if session is None:
        session = aiohttp.ClientSession()
        async with session.get(url) as resp:
            response_text = await resp.text()
        await session.close()
    else:
        async with session.get(url) as resp:
            response_text = await resp.text()

    p = ParseConnections(response_text)

    logger.debug(p)

    return p

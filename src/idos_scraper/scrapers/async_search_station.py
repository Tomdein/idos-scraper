import aiohttp
import urllib.parse

from .. import log
from .search_station import _GetQueryStationSearch, _ParseStationSearchResponse

# create logger
logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)
logger.addHandler(log.ch)

# -------------------- Setting up logging --------------------

async def async_SearchStation(station_short_str: str,
                              number_of_hints_to_query: str | int = 3,
                              session: aiohttp.ClientSession | None = None
                              ) -> list | None:
    station_search_query = _GetQueryStationSearch(station_short_str, number_of_hints_to_query)

    url = station_search_query["url"] + "?" + urllib.parse.urlencode(station_search_query["querystring"], doseq=False)

    logger.debug(url)

    if session is None:
        session = aiohttp.ClientSession()
        async with session.get(url) as resp:
            response_text = await resp.text()
        await session.close()
    else:
        async with session.get(url) as resp:
            response_text = await resp.text()

    return _ParseStationSearchResponse(response_text)

import aiohttp
import urllib.parse

from .. import log
from .search_connections import ParseConnectionsDetails
from .page_connections import _GetQueryPaging, _ParsePagingResponse

# create logger
logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)
logger.addHandler(log.ch)

async def async_PageConnections(ids_list: list,
                                handle: int,
                                arrivalThere: str,
                                searchDate: str,
                                session: aiohttp.ClientSession | None = None
                                ) -> dict | None:
    paging_query = _GetQueryPaging(ids_list, handle, arrivalThere, searchDate)
    
    url = paging_query["url"] + "?" + urllib.parse.urlencode(paging_query["querystring"], doseq=False)
    
    logger.debug(url)

    if session is None:
        session = aiohttp.ClientSession()
        async with session.post(url, data=paging_query["payload"]) as resp:
            response_text = await resp.text()
        await session.close()
    else:
        async with session.post(url, data=paging_query["payload"]) as resp:
            response_text = await resp.text()

    return _ParsePagingResponse(response_text)

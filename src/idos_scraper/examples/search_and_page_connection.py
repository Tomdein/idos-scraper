import idos_scraper.log as log

# create logger
logger = log.logging.getLogger(__name__)
logger.addHandler(log.ch)

if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.

    from idos_scraper import scrapers

    query = scrapers.SearchConnectionsByStation(time="18:20")

    for i in range(0,10):
        ids_list = [connection["id"] for connection in query["connections"]]
        paged_query = scrapers.PageConnections(ids_list, query["connResult"]["handle"], query["connResult"]["arrivalThere"], query["connResult"]["searchDate"])

        query["connResult"]["connData"].extend(paged_query["connResult"]["connData"])
        query["connections"].extend(paged_query["connections"])
        # ?: Merge query["connResult"]["legend"]?

    for i, connection in enumerate(query["connections"]):
        logger.debug(f"Connection {i}:")
        logger.debug(f"\t{connection}")

else:
    logger.critical("Run examples as '__main__' instead of importing. Run them as `python3 -m idos-scraper.examples.<EXAMPLE_NAME>`")
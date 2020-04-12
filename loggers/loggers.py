from loguru import logger


def make_filter(name):
    def f(record):
        return record["extra"].get("name") == name

    return f


logger.add("../loggers/games.log", level="DEBUG", filter=make_filter("games"))
logger.add("../loggers/requests.log", level="DEBUG", filter=make_filter("requests"))
logger.add("../loggers/stats.log", level="DEBUG", filter=make_filter("stats"))

games_logger = logger.bind(name="games")
requests_logger = logger.bind(name="requests")
stats_logger = logger.bind(name="stats")

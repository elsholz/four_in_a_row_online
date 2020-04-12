from loguru import logger


def make_filter(name):
    def f(record):
        return record["extra"].get("name") == name

    return f


logger.add("../logs/games.log", level="DEBUG", filter=make_filter("games"))
logger.add("../logs/requests.log", level="DEBUG", filter=make_filter("requests"))
logger.add("../logs/stats.log", level="DEBUG", filter=make_filter("stats"))

games_logger = logger.bind(name="games")
requests_logger = logger.bind(name="requests")
stats_logger = logger.bind(name="stats")

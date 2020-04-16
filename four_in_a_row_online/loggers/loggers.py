from loguru import logger
import pathlib


def make_filter(name):
    def f(record):
        return record["extra"].get("name") == name

    return f


loggers_path = pathlib.Path(__file__).parent.absolute()

logger.add(f"{loggers_path}/games.log", level="DEBUG", filter=make_filter("games"))
logger.add(f"{loggers_path}/requests.log", level="DEBUG", filter=make_filter("requests"))
logger.add(f"{loggers_path}/stats.log", level="DEBUG", filter=make_filter("stats"))

games_logger = logger.bind(name="games")
requests_logger = logger.bind(name="requests")
stats_logger = logger.bind(name="stats")

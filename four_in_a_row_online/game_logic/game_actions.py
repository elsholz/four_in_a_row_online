from enum import Enum


class ActionType(Enum):
    place_token = "PLACE_TOKEN"

    def __str__(self):
        return self.value

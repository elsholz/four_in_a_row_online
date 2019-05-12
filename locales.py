

import enum

class Languages(enum.Enum):
    german = 'German'
    english = 'English'


Locales = {
    'exceptions': [
        {
            'Not all players are ready': {
                Languages.german: 'Nicht alle Spieler sind breit!'
            }
        },
        {
            'Not enough players': {
                Languages.german: 'Nicht genügend Spieler!'
            }
        },
    ],
    'rules': [
        {
            'Shuffle turn order on start': {
                Languages.german: 'Spielreihenfolge mischen'
            }
        },
        {
            'Enable Chat': {
                Languages.german: 'Klatsch und Tratsch erlauben'
            }
        },
    ]
}

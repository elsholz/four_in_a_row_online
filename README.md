# four_in_a_row_online
## What is it?
Four in a Row Online is a free and Open Source Multiplayer Online Game. The Goal of the game is to provide a decent dose of fun to everyone who plays it, be it with or without their friends (assuming they have some). The architecture of the game is kept simple and might become more complex in advanced stages of development. Ultimately, players should be able to determine as much of the game mechanics as possible by theirselves, hence, future extensions are quite possible and add to a unique experience. The Game is currently in an early stage of development.

## Frontend
The Frontend is based on `snap.svg` and `vue.js`. All menus will be created using `vue.js` and the component framework `vuetify`. The central gameplay item, that is the play field, will be rendered using `snap.svg`, which allows for a huge amount of customization and easy animation of svg items.

## Backend
The Backend is also made of 2 parts. Requests will be handled by a `Flask` server, whereas game logic will be processed by a `Python` program.

## Directory Structure

/four_in_a_row_online
- `data` contains data that is shared between backend and frontend. Maps constants to text subject to future change, e.g. lovalization.
- `frontend` the frontend based on vuejs and vuetify.
- `game_logic` the game logic which is invoked by the backend.
- `backend` the backend to receive websocket connections and proxies requests to the game logic.
	


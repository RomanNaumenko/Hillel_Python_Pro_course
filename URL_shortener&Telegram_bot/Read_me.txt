	This little project is URL shortener(service example:"https://www.shorturl.at/") wrote with AioHTTP.
The main endpoint displays the form by GET with a field to store the link, POST stores and displays 
the ID of the stored record. The second endpoint uses the saved link ID. it selects the correct link 
and redirects to it. 
	Also as a bonus made a link shortener bot (library https://github.com/aiogram/aiogram).The bot features:

	- process and react the start command.
	- when the link arrives -> save it and give the id
	- when id arrives -> return saved link
(predicted URL can looks like http:// or https://, store information about this in the database).
	Besides that that bot and app can work from Docker. In project took places docker-compose.yml and Dockerfile,
and .env files. One container for the base, a container for a web application and container for the bot.


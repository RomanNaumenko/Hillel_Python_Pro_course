	This project was my first interaction with Django framework. In order to save time I have post this 
project here complete in it`s final version. Didn`t want to do it step-by-step like I did with previous 
Flask-project. In a few words, this project is some kind of tourist guide that offers to users different tourist 
routes(this routes can be different types, time to beat them, each one lies on trought individual locations and 
etc.) and makes a reservation for them. 
	Project truly lacks proper documentation so I try to describe it here. Features of the project:

	- It provides basic user interface that bring to users all needed information about route that they 
interested in. Using ORM DB queries and specific filter endpoints help to show user proper information about route 
and it`s event. As a result of receiving the route, user also see the names of the starting and ending location 
points, as a result of receiving the event - information about the route to which the event belongs;

	- Users can login/logout, project gives specific permissions to every user depends from one`s status(user, 
admin, etc.)

	- Project operates with two DB(MongoDB and Postgresql) that make it possible to storage and receive necessary 
information fast and in a proper way;

	- Added validation for specifying the date for model event (data should be later than now) and also added 
pagination when receiving routes (including when filtering) for more comfortable and realistic visual;

	- For this project were created a few tests(used Mock, Django tests, Django test fixtures) that can be helpful
for understanding how endpoints work and checking it for working correctly.
# Exponea-challenge

This API is made as part of hiring process into Exponea. Purpose of this API is to view responses from Exponea test server.
API was made by django RESTframework. Django RESTFramework is not necessary the best option for this kind of project, because it is really robust for this small size of project, 
but it makes creating API views and testing much easier to implement and Django is framework I am most familiar with.

# Installation guide
pull this repository and cd into it
sudo docker build -t exponea_image .
sudo docker run -p 80:80 exponea_image
you should have app running on port 80 
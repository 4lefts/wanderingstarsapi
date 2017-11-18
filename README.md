# wandering stars
## a python web api for solar system data

A simple REST api for getting the altitude and azimuth of the following solar system objects:

* The Sun
* The Moon
* The planets (excluding Earth)
* The Gililean satelites (coming soon)

In addition, metadata are returned that give:

* The latitude and longitude of the request
* The time of the request in local time and UTC
* The timezone for the latitude and longitude of the request (areas not in any country (e.g. those at sea), will return "null")

The API can be accessed by sending a get request to /api/latitude/longitude, e.g. api/50.7/-3.5 for Exeter, Devon, UK.

In development activate venv and install ```requirements.txt```, set environment variables to ```FLASK_APP=ephemApi.py``` and ```FLASK_DEBUG=1```, for development, then ```flask run```.

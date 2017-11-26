import math
from datetime import datetime
import pytz
import ephem
from tzwhere import tzwhere
from flask import Flask, url_for, request, render_template, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#used for template footer:
now = datetime.now()
year = now.year


@app.route('/')
def index():
    initialLat = 0
    try:
        initialLat = request.cookies.get('current_lat')
    except:
        initialLat = 50.7

    initialLong = 0
    try:
        initialLong = request.cookies.get('current_long')
    except:
        initialLong = -3.5

    # return render_template("index.html", title="Wandering Stars", year=year, initialLat=initialLat, initialLong=initialLong)
    return render_template("index.html", title="Wandering Stars", year=year)

@app.route('/api/<string:latitude>/<string:longitude>', methods=['GET'])
def get_data(latitude, longitude):
    updateLocation(latitude, longitude)
    data = computeData(observer, bodies)
    resp = make_response(jsonify(data))
    resp.set_cookie('current_lat', latitude)
    resp.set_cookie('current_long', longitude)
    return resp

###############################################
# Logic for getting and returning alt/az data #
###############################################

observer = ephem.Observer()
observer.lat = '0'
observer.lon = '0'

# array of bodies to compute
bodies = [
    ephem.Sun(),
    ephem.Moon(),
    ephem.Mercury(),
    ephem.Venus(),
    ephem.Mars(),
    ephem.Jupiter(),
    ephem.Saturn(),
    ephem.Uranus(),
    ephem.Neptune()
]

# check inputs are numbers and in range etc
# update location if they are
def updateLocation(lat, lon):
    # check that the latitude input is a number
    try:
        tempLat = float(lat)
        if -90 < tempLat < 90:
            #set latitude as a string
            observer.lat = lat
        else:
            observer.lat = '0'
    except:
        observer.lat = '0'

    # check that the longitude input is a number
    try:
        tempLon = float(lon)
        if -180 < tempLon < 180:
            #set longitude as a string
            observer.lon = lon
        else:
            observer.lon = '0'
    except:
        observer.lon = '0'
    return

def utc_to_local(t, tz):
    return t.astimezone(pytz.timezone(tz))

def computeData(obs, bs):
    # initialise dicts to return
    ret = {}
    meta = {}
    bodies = []

    # set metadata for observer
    tz = getTz(obs)
    utc = ephem.now().datetime()
    ret["meta"] = meta
    meta["utc"] = str(ephem.now())
    meta["lat"] = str(obs.lat)
    meta["lon"] = str(obs.lon)
    meta["tz"] = tz
    meta["localtime"] = str(utc_to_local(utc, tz)) 

    # compute data for each object
    for body in bs:
        bodyData = {}
        obs.date = ephem.now()
        body.compute(obs)
        bodyData["name"] = body.name
        bodyData["alt"] = str(body.alt)
        bodyData["az"] = str(body.az)
        # set rise or set key depending on current alt
        if body.alt > 0:
            bodyData["set"] = str(utc_to_local((obs.next_setting(body)).datetime(), tz))
        elif body.alt <= 0:
            bodyData["rise"] = str(utc_to_local((obs.next_rising(body)).datetime(), tz))
        if bodyData["name"] == "Moon":
            bodyData["phase"] = body.moon_phase
        if bodyData["name"] == "Saturn":
            #tilt of rings toward earth (positive = southward, negative = northward)
            bodyData["tilt"] = body.earth_tilt
        bodies.append(bodyData)

    # add all bodies to return dict
    ret["bodies"] = bodies
    return ret

####################################
# Logic for getting timezone  data #
####################################

tzwhere = tzwhere.tzwhere()
def getTz(obs):
    tzStr = tzwhere.tzNameAt(math.degrees(obs.lat), math.degrees(obs.lon))
    return tzStr

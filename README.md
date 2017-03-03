# Meat N' Eat API

**Host**<br />
Udacity

**Course**<br />
Designing RESTFul APIs

**Exercise**<br />
Final project

**Description**<br />
Meet N’ Eat is a social application for meeting people based on their food interests<br />

**Features**
* Meet N’ Eat leverages the Google Maps API and Foursquare API in order to find a restaurant for users and geocode 
locations into latitude and longitude coordinates.
* Users are able to log in with either a username/password combination or using an OAuth provider 
like Google or Facebook. The application generates it’s own tokens for users.
* All endpoints use rate limiting to prevent abuse of your API.
* Documentation for the API is created in a way that is developer friendly and
aesthetically pleasing.

**Run app**
* Clone app: git clone https://github.com/stijnblommerde/meat_n_eat_api.git
* Add virtual environment: virtualenv -p python3 env
* Install requirements: pip install -r requirements.txt
* Run server: python manage.py runserver
* Access API via requests, for instance using POSTMAN

**Run tests**
* Get key for using Google Maps Geocoding API: https://developers.google.com/maps/documentation/geocoding/start
* Get Id secret for using Foursquare API: foursquare.com > create account > receive credentials
* create and load environmental vars: 
..*MEAT_N_EAT_CONFIG='testing'
..*GOOGLE_API_KEY='your Google key' 
..*FOURSQUARE_CLIENT_ID='your foursquare client id'
..*FOURSQUARE_CLIENT_SECRET='your foursquare client secret'
* run server: python manage.py runserver
* run tests: python manage.py test
* 


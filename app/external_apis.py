import httplib2
import json
from flask import current_app


def get_geocode_location(location_string):
    """ Use Google Maps to convert a location into Latitude/Longitude coordinates

    FORMAT: https://maps.googleapis.com/maps/api/geocode/json?
    address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY

    :param location_string:
    :return: latitude and longitude of location string
    """
    if not location_string:
        return None, None
    location_string = location_string.replace(" ", "+")
    url = (
        'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'
        % (location_string, current_app.config['GOOGLE_API_KEY']))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1].decode('utf-8'))

    # invalid request
    if len(result['results']) == 0:
        return result['error_message']

    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return latitude,longitude


def find_restaurant(mealType, location_string):
    # 1. Use getGeocodeLocation to get the latitude and longitude coordinates
    # of the location string.
    lat_long = get_geocode_location(location_string)
    ll = str(lat_long[0]) + ',' + str(lat_long[1])

    # 2.  Use foursquare API to find a nearby restaurant with the latitude,
    # longitude, and mealType strings.
    url = "https://api.foursquare.com/v2/venues/search?client_id={id}" \
          "&client_secret={secret}&v={v}&ll={ll}&intent={intent}" \
          "&radius={radius}&query={query}".format(
        id=current_app.config['FOURSQUARE_CLIENT_ID'],
        secret=current_app.config['FOURSQUARE_CLIENT_SECRET'],
        v=current_app.config['FOURSQUARE_VERSION'], ll=ll,
        intent=current_app.config['FOURSQUARE_INTENT'],
        radius=current_app.config['FOURSQUARE_RADIUS'], query=mealType
    )
    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    result = json.loads(content.decode('utf-8'))

    # invalid request
    if result['meta']['code'] != 200:
        print('result:', result)
        return result['meta']['errorDetail']

    # 3. Grab the first restaurant
    if result['response']['venues']:
        restaurant = result['response']['venues'][0]
        restaurant_name = restaurant['name']
        restaurant_id = restaurant['id']
        restaurant_address_list = restaurant['location'] \
            ['formattedAddress']
        address = ''
        for part in restaurant_address_list:
            address += part + ', '
        restaurant_address = address.rstrip(', ')

        # 4. Get a  300x300 picture of the restaurant using the venue_id
        # (you can change this by altering the 300x300 value in the URL or
        # replacing it with 'orginal' to get the original picture
        url = "https://api.foursquare.com/v2/venues/{venue_id}/photos?" \
              "client_id={client_id}&client_secret={client_secret}&v={v}". \
            format(venue_id=restaurant_id,
                   client_id=current_app.config['FOURSQUARE_CLIENT_ID'],
                   client_secret=current_app.config['FOURSQUARE_CLIENT_SECRET'],
                   v=current_app.config['FOURSQUARE_VERSION'])
        response, content = h.request(url, 'GET')
        result = json.loads(content.decode('utf-8'))

        # 5. Grab the first image
        if result['response']['photos']['items']:
            first_image = result['response']['photos']['items'][0]
            prefix = first_image['prefix']
            size = '300x300'
            suffix = first_image['suffix']
            image_url = prefix + size + suffix

        # 6. If no image is available, insert default a image url
        else:
            image_url = "http://lauderdaleyachtcharters.com/wp-content/" \
                        "uploads/2015/12/foursquare-icon--300x300.png"

        # 7. Return a dictionary containing the restaurant name, address,
        # and image url
        return {'restaurant_name': restaurant_name,
                'address': restaurant_address,
                'image_url': image_url}
    else:
        return None
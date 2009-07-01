# -*- coding: utf-8 -*-
# Copyright (c) 2009 GOcipher.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import urllib2
import urllib

from contactmaps.models import City
from google.appengine.ext import db

try:
  import json
except ImportError:
  from django.utils import simplejson as json

def get_geoinfo(query):
    """
    This function queries the GoogleMaps Geocoding server,
    and retrieves the query's geo position (that is, its
    latitude and longitude).
    
    If no info was found for the query, this function returns
    None
    """
    GOOGLE_MAPS_API_URL = "http://maps.google.com/maps/geo?"
    GOOGLE_MAPS_KEY = 'ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSosDVG8KKPE1-m51RBrvYughuyMxQ-i1QfUnH94QxWIa6N4U6MouMmBA'
    GOOGLE_MAPS_SENSOR = 'false'
    GOOGLE_MAPS_OUTPUT = 'json'
    
    quoted_query = urllib.quote_plus(query.encode('utf8', 'replace'), ',')
    values = {
        'q' : quoted_query,
        'output': GOOGLE_MAPS_OUTPUT,
        'oe': 'utf8',
        'key': GOOGLE_MAPS_KEY,
        'sensor': GOOGLE_MAPS_SENSOR
    }
    data = urllib.urlencode(values)
    url = GOOGLE_MAPS_API_URL + data
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    response_data = unicode(response.read(), 'utf-8', 'replace')
    try:
        json_response = json.loads( response_data.encode('ascii', 'ignore') )
    except:
        return None
    finally:
        response.close()
    
    code = json_response['Status']['code']
    if code == 200:
        longitude = json_response["Placemark"][0]["Point"]["coordinates"][0]
        latitude = json_response["Placemark"][0]["Point"]["coordinates"][1]
        return  {'latitude'  : latitude, 'longitude' : longitude}
    else:
        return None
    
def store_city_from_contact(contact):
    """
    This function receives a contact parameter, which is an
    entity of type 'Contact', and stores it in the DataStore 
    along with is geographical location.
    """
    # If we don't have the contact's city yet, save it, along with its geo info
    total_city_records = (
        City.all().
        filter('name =', contact.city).
        filter('state =', contact.state).
        filter('country = ', contact.country).
        count()
    )
    if total_city_records == 0 and contact.city is not None:
        location = get_geoinfo(contact.city)
        
        # Store the city only if its geo location is available.
        if location:
            City(
                name=contact.city,
                state=contact.state,
                country=contact.country,
                location=db.GeoPt(location['latitude'], location['longitude'])
            ).put()

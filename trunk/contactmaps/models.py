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

"""
ContactMaps application models.
"""
__docformat__ = 'epytext en'


###############################################################################
## Imports
###############################################################################
from django.db.models import permalink
from google.appengine.ext import db

###############################################################################
## Models
###############################################################################
class Contact(db.Model):
    """
    Basic Contact profile
    """
    owner = db.UserProperty()
    name = db.StringProperty(required=True)
    company = db.StringProperty()
    address = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    country = db.StringProperty()
    zip_code = db.StringProperty()
    location = db.GeoPtProperty()
    creation_date = db.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('contactmaps.views.show_contact', (), {'key': self.key()})

class City(db.Model):
    """
    This model stores the cities, along with their state and country
    (there seems to be cities with the same name, but located in
    different countries).
    
    This model also stores the geographic location of the city, which
    is calculated by an appengine CRON process.
    """
    name = db.StringProperty(required=True)
    state = db.StringProperty()
    country = db.StringProperty()
    location = db.GeoPtProperty()

    def __unicode__(self):
        return self.name
    
class ContactmapsImport(db.Model):
    """
    This model stores the FreshBooks usernames from which the owner
    account has already imported Contacts.
    """
    owner = db.UserProperty(required=True)
    freshbooks_username = db.StringProperty(required=True)


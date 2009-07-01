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
ContactMaps form to add and edit Contacts. This module uses django forms.

@todo: Recalculate geoinfo when a Contact is edited
"""
__docformat__ = 'epytext en'


###############################################################################
## Imports
###############################################################################
from django import forms
from contactmaps.app import get_geoinfo, store_city_from_contact
from contactmaps.models import Contact
from google.appengine.api import users
from google.appengine.ext import db

###############################################################################
## Forms
###############################################################################
class ContactForm(forms.ModelForm):
    def save(self):
        """
        This method sets the owner of the newly created
        contact to the current google user.
        
        It also calculates the geographic location of both the
        new contact and the new contact's city.
        """
        contact = super(ContactForm, self).save(commit=False)
        store_city_from_contact(contact)
        
        location = get_geoinfo(
            '%s, %s, %s, %s' %
            (contact.address, contact.city, contact.state, contact.country)
        )
        
        if location is not None:
            contact.location=db.GeoPt(location['latitude'], location['longitude'])
        
        contact.owner = users.get_current_user()
        contact.save()
        
        return contact
    
    class Meta:
        model = Contact
        exclude = ('owner', 'location', 'creation_date')

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

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, \
     update_object
from gaegene.pagination.models import Paginator, Page
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.ext import db
from contactmaps.forms import ContactForm
from contactmaps.lib import freshbooks
from contactmaps.models import City, Contact, ContactmapsImport
from contactmaps.app import get_geoinfo, store_city_from_contact
from ragendja.auth.views import google_logout
from ragendja.template import render_to_response

try:
    from google.appengine.api.labs import taskqueue
except ImportError:
    from google.appengine.api import taskqueue

try:
  import json
except ImportError:
  from django.utils import simplejson as json

###############################################################################
## General Views
###############################################################################
def index(request):
    """This view just displays the welcome page"""
    return render_to_response(request, 'main.html')

@login_required
def logout(request):
    """This view logs the user out from google."""
    return google_logout(request, next_page=reverse('index'))

###############################################################################
## CRUD Views
###############################################################################
@login_required
def show_contact(request, key):
    """
    Shows details about a specific contact.
    
    It uses django's generic views.
    """
    return object_detail(request, Contact.all(), key)

@login_required
def list_contacts(request):
    """
    The list of contacts. This view also fetches the cities
    that the current contacts live in and the geographical postion
    of those cities.
    
    It uses the gaegene library for pagination.
    """
    PAGINATE_BY = 20
    contacts = Contact.all().filter("owner =", users.get_current_user()).order('creation_date')
    
    # Paginate
    paginator = Paginator(contacts, 'creation_date', per_page=PAGINATE_BY)
    page_value = request.GET.get('page')
    page = paginator.page(page_value)
    paginated_contacts = page.object_list
    
    # Get the cities that the contacts live in
    _cities = []
    for contact in paginated_contacts:
        _cities.append(contact.city)
    cities = set(_cities)
    
    cities_list = []
    if len(cities):
        # Construct the cities string for our query
        cities_str = u'('
        for city in cities:
            cities_str += "'%s'," % city
        cities_str = cities_str.strip(',')
        cities_str += u')'
        
        # Create the cities query
        for city in City.gql("WHERE name IN %s" % cities_str):
            cities_list.append({
                'name': city.name,
                'latitude': city.location.lat,
                'longitude': city.location.lon
            })
    
    return object_list(
        request,
        contacts,
        paginate_by=PAGINATE_BY,
        extra_context={'cities_list': cities_list}
    )

@login_required
def add_contact(request):
    """
    Adds a new contact.
    
    It uses django's generic views
    """
    return create_object(
        request, form_class=ContactForm,
        post_save_redirect=reverse(
            'contactmaps.views.show_contact',
            kwargs=dict(key='%(key)s')
        )
    )

@login_required
def edit_contact(request, key):
    """
    Edits the information of a specific contact, identified by the
    'key' parameter.
    
    It uses django's generic views.
    """
    return update_object(request, object_id=key, form_class=ContactForm)

@login_required
def delete_contact(request, key):
    """
    Deletes a contact, identified by the 'key' parameter.
    
    It uses django's generic views.
    """
    return delete_object(
        request, Contact, object_id=key,
        post_delete_redirect=reverse('contactmaps.views.list_contacts')
    )

###############################################################################
## Additional Views: Delete all contacts and import contacts from Freshbooks
###############################################################################
@login_required
def delete_contacts(request):
    """
    Deletes all the contacts from the current google username.
    
    This view also deletes the entities associated with the contacts
    that are being deleted.
    """
        
    if request.method == 'POST':
        db.delete( Contact.all().filter("owner =", users.get_current_user()) )
        db.delete( ContactmapsImport.all().filter("owner =", users.get_current_user()) )
        return HttpResponseRedirect(reverse('contactmaps.views.list_contacts'))
    else:
        return render_to_response(
            request,
            'contact_confirm_delete.html',
            {'object': {'name': 'All contacts', 'key': 'all'}}
        )

@login_required
def import_contacts_setup(request, page):
    """
    """
    # TODO: this must go in settings.py
    # Max number of contacts to fetch per page
    CONTACTS_PER_PAGE = 500
    
    # Ensure that the username and token are valid
    username = request.POST.get('username')
    token = request.POST.get('token')
    
    if None in (username, token) or '' in (username, token):
        return HttpResponse(json.dumps({
            'success': False,
            'error': 'Invalid Parameters'
        }))
    
    # Set up the Freshmaps account to import from
    freshbooks.setup('%s.freshbooks.com' % username, token)
    
    # Get the client_ids of the Contacts to import. This is done using paging
    # to overcome AppEngine restrictions
    options = {'per_page': CONTACTS_PER_PAGE, 'page': int(page)}
    try:
        contacts = [c.client_id for c in freshbooks.Client.list(options)]
    except urlfetch.DownloadError:
        return HttpResponse(
            json.dumps({
                'success': False,
                'error': 'Connection timed out',
                'retry': True
            })
        )
    except urllib2.HTTPError, error:
        if error.code == 401:
            error_msg = 'Invalid username/token'
        else:
            error_msg = 'Connection to Freshmaps refused'
        
        return HttpResponse(
            json.dumps({
                'success': False,
                'error': error_msg,
                'retry': False
            })
        )
    except:
        return HttpResponse(
            json.dumps({
                'success': False,
                'error': 'Unknown Error',
                'retry': False
            })
        )
    
    # Notify the client whether to keep proccessing client_ids
    keep_processing = True
    if len(contacts) < options['per_page']:
        keep_processing = False
    
    
    return HttpResponse(
        json.dumps({
            'success': True,
            'contacts': contacts,
            'keepProcessing': keep_processing
        })
    )

@login_required
def import_contacts(request):
    """
    """
    # Ensure that the username and token are valid
    username = request.POST.get('username')
    token = request.POST.get('token')
    
    if None in (username, token) or '' in (username, token):
        return HttpResponse(json.dumps({
            'success': False,
            'error': 'Invalid Parameters'
        }))
    
    # Ensure that we have not imported contacts from this freshbooks account
    already_imported = (
        ContactmapsImport.all().
        filter('owner =', users.get_current_user()).
        filter('freshbooks_username =', username).
        count()
    )
    if already_imported:
        return HttpResponse(json.dumps({
            'success': False,
            'error': 'Clients from the Freshmaps account %s.freshbooks.com have already been imported as contacts' % username
        }))
    
    # Other parameters
    try:
        contacts = json.loads( request.POST.get('contacts', '[]') )
    except ValueError:
        contacts = []
        
    finalize = request.POST.get('finalize')
    if finalize:
        # Mark that the current google user has already imported
        # contacts from the input freshbooks account.
        ContactmapsImport(
            owner=users.get_current_user(),
            freshbooks_username=username
        ).put()
        
        contacts = [] # Prevent processing contacts. There should be none, though
    
    
    # Set up the Freshmaps account to import from
    freshbooks.setup('%s.freshbooks.com' % username, token)
    
    for contact_id in contacts:
        _contact = freshbooks.Client.get(contact_id)
        
        _name = '%s %s' % (_contact.first_name, _contact.last_name)
        if not _name.strip():
            _name = 'Unknown Name'
                
        # Save the contact in the datastore
        contact = Contact(
            owner=users.get_current_user(),
            name=_name,
            company=_contact.organization,
            address=_contact.p_street1,
            city=_contact.p_city,
            state=_contact.p_state,
            country=_contact.p_country,
            zip_code=_contact.p_code,
        )
        contact.put()
        
        # Add a task in order to calculated the contact's geoinfo
        try:
            taskqueue.add(url='/contact-geo-info/', params={'key': contact.key()})
        except TransientError:
            taskqueue.add(url='/contact-geo-info/', params={'key': contact.key()})
    
    return HttpResponse(
        json.dumps({
            'success': True,
        })
    )

###############################################################################
## Task Queue worker
###############################################################################
def get_contact_geoinfo(request):
    """
    """
    # Ensure that the key parameter is present
    key = request.POST.get('key')
    if key is None:
        return HttpResponse(
            json.dumps({
                'success': False,
                'error': 'Key parameter not found in POST variables'
            })
        )
    
    # Get the contact entity usgin the input key
    contact = Contact.get(key)
    if contact is None:
        return HttpResponse(
            json.dumps({
                'success': False,
                'error': 'Invalid Contact key'
                })
        )
    
    # Calculate the geoinfo for the contact identified by key
    store_city_from_contact(contact)
    location = get_geoinfo(
        '%s, %s, %s, %s' %
        (contact.address, contact.city, contact.state, contact.country)
    )
    if location:
        contact.location = db.GeoPt(location['latitude'], location['longitude'])
        contact.put()
    
    return HttpResponse(
        json.dumps({
            'success': True,
        })
    )
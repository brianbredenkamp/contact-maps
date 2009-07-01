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
URLConf file.
"""
__docformat__ = 'epytext en'


###############################################################################
## Imports
###############################################################################
from django.conf.urls.defaults import *

###############################################################################
## URL patterns
###############################################################################
urlpatterns = patterns('contactmaps.views',
    (r'^$', 'list_contacts'),
    (r'^add/$', 'add_contact'),
    (r'^show/(?P<key>.+)$', 'show_contact'),
    (r'^edit/(?P<key>.+)$', 'edit_contact'),
    (r'^delete/(?P<key>.+)$', 'delete_contact'),
    (r'^deleteall/$', 'delete_contacts'),
    (r'^import/$', 'import_contacts'),
    (r'^import-setup/(\d+)/$', 'import_contacts_setup'),
)

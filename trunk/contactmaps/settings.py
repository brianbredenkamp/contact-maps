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
Settings file. This file is added to the global settings by app-engine-patch.
"""
__docformat__ = 'epytext en'


###############################################################################
## Settings
###############################################################################
LOCALDEV = False
"""This setting determines whether the project is being developed
locally (offline) or in a production-like environment"""

USE_JS_CDN = True and not LOCALDEV
"""If this setting is true, jquery and jquery ui will be fetched
from the google ajax apis CDN"""

PAGINATE_BY = 20
"""This setting states how many contacts to show in each page of 
the Contact List"""

IMPORT_SETUP_CONTACTS_PER_PAGE = 500
"""This determines how many Freshbooks client ids to fecth per 
request. AppEngine applications have a 30 second request limit 
so this setting permits avoid request errors"""

GOOGLE_MAPS_KEY = 'ABQIAAAA3LHzdmECuV8KC0ABupgtsRTQ3Oe6hoUSmR6N8-23Kt61mIn_uRQX_xMeg4U7UNMd4r5Mhi1BWxrjNg'
"""The key to use when interacting with the Google Maps API"""

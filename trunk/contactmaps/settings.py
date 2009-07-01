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
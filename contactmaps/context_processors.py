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
Template Context Processors.
"""
__docformat__ = 'epytext en'


###############################################################################
## Imports
###############################################################################
import inspect
from contactmaps import settings

###############################################################################
## Context Processors
###############################################################################
def contactmaps_settings(request):
  """
  This context processor makes the contactmaps settings available to 
  templates.
  """
  # Get the list of settings using the inspect module, taking out
  # all the python magic objects like __builtins__, __name__, etc.
  # The inspect module returns a list of tuples like:
  # [('variable_name_1', value_1), ('variable_name_n', value_n)], so we
  # use only the tuples for which their first element (i.e. index=0) does
  # not start with double underscore.
  s = [s for s in inspect.getmembers(settings) if not s[0].startswith('__')]
  
  # Make every setting available for tempaltes
  context_extras = {}
  for setting in s:
    context_extras[setting[0]] = setting[1]
  
  return context_extras

# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from contactmaps.views import index, about, logout, get_contact_geoinfo

handler500 = 'ragendja.views.server_error'

urlpatterns = auth_patterns + patterns('',
     url(r'^$', index, name='index'),
     url(r'^logout/$', logout, name='logout'),
     url(r'^about/$', about, name='about'),
     
     # Task Queue workers
     (r'^contact-geo-info/$', get_contact_geoinfo)
) + urlpatterns

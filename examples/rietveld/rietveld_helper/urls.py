from django.conf.urls.defaults import *
from django.contrib import admin

from codereview.urls import urlpatterns

admin.autodiscover()

urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': 'static/'}),
        (r'^accounts/login/$', 'django.contrib.auth.views.login'),
        (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
        ('^admin/(.*)', admin.site.root),
        ('^_ah/admin', 'rietveld_helper.views.admin_redirect'),
    )

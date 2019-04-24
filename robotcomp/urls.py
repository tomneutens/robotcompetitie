from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import os.path

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

from django.conf import settings
from django.conf.urls.static import static
import robots.views
import django.views

urlpatterns = [
    url(r'^$', robots.views.index),
    url(r'^manage_round/$', robots.views.manage_current_round),
    url(r'^manage_round/(?P<round_id>\d+)/$', robots.views.manage_round),
    url(r'^start_round/(?P<round_id>\d+)/$', robots.views.start_round),
    url(r'^finish_round/(?P<round_id>\d+)/$', robots.views.finish_round),
    url(r'^plan_round/(?P<round_id>\d+)/$', robots.views.plan_round),
    url(r'^replan_round/(?P<round_id>\d+)/$', robots.views.replan_round),
    url(r'^postpone_match/(?P<match_id>\d+)/$', robots.views.postpone_match),
    url(r'^finish_match/(?P<match_id>\d+)/$', robots.views.finish_match),
    url(r'^start_next_matches/(?P<round_id>\d+)/$', robots.views.start_next_matches),
    url(r'^frontend_data/$', robots.views.frontend_data),
    url(r'^ranking_data/$', robots.views.ranking_data),
    url(r'^public_data/$', robots.views.public_data),
    url(r'^live_display/$', robots.views.live_display),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Static file view for the frontend
    url(r'^frontend/(?P<path>.*)$', django.views.static.serve,
        {'document_root': frontend_path }),

    url(r'^fonts/(?P<path>.*)$', django.views.static.serve,
        {'document_root': frontend_path }),

    # Static file view for the media
    url(r'^media/(?P<path>.*)$', django.views.static.serve,
        {'document_root': media_path }),
]




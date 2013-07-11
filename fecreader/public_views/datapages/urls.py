from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

urlpatterns = patterns('',
        url(r'^current-senators/$', 'public_views.datapages.views.current_senators'),
        url(r'^newest-filings/$', 'public_views.datapages.views.newest_filings'),
        url(r'^newest-filings/candidates/$', 'public_views.datapages.views.newest_filings_candidates'),
        url(r'^newest-filings/ies/$', 'public_views.datapages.views.newest_filings_ies'),       
        url(r'^new-committees/$', 'public_views.datapages.views.new_committees'),
        url(r'^downloads/$', 'public_views.datapages.views.downloads'),        
)
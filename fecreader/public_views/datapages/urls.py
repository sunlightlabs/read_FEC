from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

urlpatterns = patterns('',
        url(r'^house/$', 'public_views.datapages.views.house'),
        url(r'^senate/$', 'public_views.datapages.views.senate'),
        url(r'^districts/$', 'public_views.datapages.views.districts'),        
        url(r'^newest-filings/$', 'public_views.datapages.views.newest_filings'),
        url(r'^newest-filings/candidates/$', 'public_views.datapages.views.newest_filings_candidates'),
        url(r'^newest-filings/ies/$', 'public_views.datapages.views.newest_filings_ies'),       
        url(r'^new-committees/$', 'public_views.datapages.views.new_committees'),
        url(r'^downloads/$', 'public_views.datapages.views.downloads'),        
        url(r'^alerts/$', 'public_views.datapages.views.alerts'),   
        url(r'^candidates/$', 'public_views.datapages.views.candidates'),   
        url(r'^reports/$', 'public_views.datapages.views.reports'),   
        url(r'^pacs/$', 'public_views.datapages.views.pacs'),         
        url(r'^outside-spending/$', 'public_views.datapages.views.outside_spending'),
)
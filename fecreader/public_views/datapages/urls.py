from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

urlpatterns = patterns('',
        url(r'^house/$', 'public_views.datapages.views.house'),
        url(r'^senate/$', 'public_views.datapages.views.senate'),
        url(r'^races/$', 'public_views.datapages.views.races'),        
        url(r'^newest-filings/$', 'public_views.datapages.views.newest_filings'),
        url(r'^new-committees/$', 'public_views.datapages.views.new_committees'),
        url(r'^download-index/$', 'public_views.datapages.views.downloads'),        
        url(r'^alerts/$', 'public_views.datapages.views.alerts'),   
        url(r'^candidates/$', 'public_views.datapages.views.candidates'),   
        url(r'^reports/$', 'public_views.datapages.views.reports'),   
        url(r'^pacs/$', 'public_views.datapages.views.pacs'),         
        url(r'^outside-spending/$', 'public_views.datapages.views.outside_spending'),
        url(r'^newbase/$', 'public_views.datapages.views.newbase'),
        url(r'^filings/(\d+)/SA/$', 'public_views.datapages.views.filings_skeda'),
        url(r'^filings/(\d+)/SB/$', 'public_views.datapages.views.filings_skedb'),
        url(r'^filings/(\d+)/$', 'public_views.datapages.views.filing'),
        url(r'^committee/[\w-]+\/(?P<committee_id>[\w\d]+)\/?$', 'public_views.datapages.views.committee'),
        url(r'^candidate/[\w-]+\/(?P<candidate_id>[\w\d]+)\/?$', 'public_views.datapages.views.candidate'),        
)
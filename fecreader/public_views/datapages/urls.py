from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

urlpatterns = patterns('',
        url(r'^house/$', 'public_views.datapages.views.house'),
        url(r'^senate/$', 'public_views.datapages.views.senate'),
        url(r'^races/$', 'public_views.datapages.views.races'),        
        url(r'^newest-filings/$', 'public_views.datapages.views.newest_filings'),
        url(r'^newest-filings/candidacy/$', 'public_views.datapages.views.newest_filings_candidacy'),
        url(r'^newest-filings/candidate-filings/$', 'public_views.datapages.views.newest_filings_candidate_filings'),
        url(r'^newest-filings/ies/$', 'public_views.datapages.views.newest_filings_ies'),       
        url(r'^new-committees/$', 'public_views.datapages.views.new_committees'),
        url(r'^download-index/$', 'public_views.datapages.views.downloads'),        
        url(r'^alerts/$', 'public_views.datapages.views.alerts'),   
        url(r'^candidates/$', 'public_views.datapages.views.candidates'),   
        url(r'^reports/$', 'public_views.datapages.views.reports'),   
        url(r'^pacs/$', 'public_views.datapages.views.pacs'),         
        url(r'^outside-spending/$', 'public_views.datapages.views.outside_spending'),
        url(r'^newbase/$', 'public_views.datapages.views.newbase'),
        url(r'^filings/(\d+)/SA/$', 'public_views.datapages.views.filings_skeda'),
)
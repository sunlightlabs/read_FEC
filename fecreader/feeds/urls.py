from django.conf.urls import patterns, include, url

from feeds import FilingFeed, FilingsFeed, FilingsFormFeed, FilingsForms, CommitteeFormsFeed, SuperpacsForms, IEFeed, IEFeedMin


urlpatterns = patterns('',
    url(r'^committee\/(?P<committee_id>C\d+)/$', FilingFeed()),    
    url(r'^committee\/(?P<committee_id>C\d+)/forms/(?P<form_types>[\w\d\-]+)/$', CommitteeFormsFeed()),
    url(r'^committees\/(?P<committee_ids>[C\d\-]+)/$', FilingsFeed()),      
    url(r'^committees\/(?P<committee_ids>[C\d\-]+)/forms/(?P<form_types>[\w\d\-]+)/$', FilingsFormFeed()),
    url(r'^forms/(?P<form_types>[\w\d\-]+)/$', FilingsForms()),
    url(r'^superpacs\/forms/(?P<form_types>[\w\d\-]+)/$', SuperpacsForms()),
    url(r'^independent-expenditures\/$', IEFeed()),
    url(r'^independent-expenditures\/(?P<min_spent>[\d]+)/$', IEFeedMin()),      
    
)
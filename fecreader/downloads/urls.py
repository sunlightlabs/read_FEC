from django.conf.urls.defaults import url, patterns



urlpatterns = patterns('',
        url(r'^filing/(?P<filing_number>[\d]+)/(?P<sked>[ABE])/', 'downloads.views.get_filing'),
        url(r'^filing/(?P<committee_id>[\d]+)/(?P<sked>[ABE])/', 'downloads.views.get_committee'),
        url(r'^taskstatus/(?P<task_id>[\w\d\-]+)/', 'downloads.views.get_task_status'),
        url(r'^build_file/(?P<task_id>[\w\d\-]+)/', 'downloads.views.build_file'),

#        url(r'^preview/(?P<fec_id>[\w\d]+)/$', 'reconciliation.views.preview'),
#        url(r'^(?P<reconciliation_type>[\w\-]+)/$', 'reconciliation.views.refine'),
#        url(r'^json/(?P<reconciliation_type>[\w\-]+)/$', 'reconciliation.views.refine_json'),
)
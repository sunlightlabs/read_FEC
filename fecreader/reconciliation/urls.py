from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('',
        url(r'^preview/(?P<fec_id>[\w\d]+)/$', 'reconciliation.views.preview'),
        url(r'^(?P<reconciliation_type>[\w\-]+)/$', 'reconciliation.views.refine'),
        url(r'^json/(?P<reconciliation_type>[\w\-]+)/$', 'reconciliation.views.refine_json'),
)
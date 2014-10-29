from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView


urlpatterns = patterns('',
        url(r'^house/$', 'public_views.datapages.views.house'),
        url(r'^senate/$', 'public_views.datapages.views.senate'),
        url(r'^races/$', 'public_views.datapages.views.races'),        
        url(r'^newest-filings/$', 'public_views.datapages.views.newest_filings'),
        url(r'^outside-spenders/$', 'public_views.datapages.views.outside_spenders'),
        # make this the home page--will need a canonical url if we deploy like this. 
        url(r'^$', 'public_views.datapages.views.home_page'),
        url(r'^new-committees/$', 'public_views.datapages.views.new_committees'),
        url(r'^download-index/$', 'public_views.datapages.views.downloads'),        
        url(r'^about/$', 'public_views.datapages.views.about'),
        url(r'^alerts/$', 'public_views.datapages.views.subscribe'), 
        url(r'^subscribe/committee_search/$', 'public_views.datapages.views.committee_search_html'), 
        url(r'^pacs/$', 'public_views.datapages.views.pacs'),         
        url(r'^outside-spending2/$', 'public_views.datapages.views.outside_spending'),
        url(r'^outside-spending/$', 'public_views.datapages.views.dynamic_ies'),
        url(r'^newbase/$', 'public_views.datapages.views.newbase'),
        url(r'^filings/(\d+)/[sS][aA]\/?$', 'public_views.datapages.views.filings_skeda'),
        url(r'^filings/(\d+)/[sS][bB]\/?$', 'public_views.datapages.views.filings_skedb'),
        url(r'^filings/(\d+)/[sS][eE]\/?$', 'public_views.datapages.views.filings_skede'),
        url(r'^filings/(\d+)/$', 'public_views.datapages.views.filing'),
        url(r'^committee/[\w-]+\/(?P<committee_id>[\w\d]+)\/?$', 'public_views.datapages.views.committee'),
        url(r'^candidate/[\w-]+\/(?P<candidate_id>[\w\d]+)\/?$', 'public_views.datapages.views.candidate'),        
        url(r'^race/(?P<cycle>\d\d\d\d)\/H\/(?P<state>\w\w)\/(?P<district>\d+)\/', 'public_views.datapages.views.house_race'),
        url(r'^race/(?P<cycle>\d\d\d\d)\/S\/(?P<state>\w\w)\/(?P<term_class>\d+)\/', 'public_views.datapages.views.senate_race'),
        url(r'^race_id/(?P<race_id>\d+)\/$', 'public_views.datapages.views.race_id_redirect'),
        url(r'^competitive-primaries\/$', TemplateView.as_view(template_name='generated_pages/primary_list_template.html')),
        url(r'^top-races\/week\/(\d+)\/$','public_views.datapages.views.top_races'),
        url(r'^top-races\/$','public_views.datapages.views.top_current_races'),
        url(r'^election-calendar\/$','public_views.datapages.views.election_calendar'),
        url(r'^overview\/super-pacs\/$', TemplateView.as_view(template_name='generated_pages/overview_superpac_template.html')),
        url(r'^overview\/outside-money\/$', TemplateView.as_view(template_name='generated_pages/overview_outside_money_template.html')),
        url(r'^overview\/dark-money\/$', TemplateView.as_view(template_name='generated_pages/overview_dark_money_template.html')),
        url(r'^overview\/connected\/$', TemplateView.as_view(template_name='generated_pages/overview_connected_template.html')),
        url(r'^overview\/$', TemplateView.as_view(template_name='generated_pages/overview_main_template.html')),
        url(r'^training\/$', TemplateView.as_view(template_name='datapages/training.html')),
        url(r'^chart_test\/(\w+)\/$','public_views.datapages.views.chart_test'),
        url(r'^charts\/spending/([\d\-]+)\/(\w+)\/$','public_views.datapages.views.weekly_comparison'),
        url(r'^charts\/spending-cumulative/([\d\-]+)\/(\w+)\/$','public_views.datapages.views.weekly_comparison_cumulative'),
        url(r'^charts\/contributions/([\d\-]+)\/(\w+)\/$','public_views.datapages.views.contrib_comparison'),
        url(r'^charts\/contributions-cumulative/([\d\-]+)\/(\w+)\/$','public_views.datapages.views.contrib_comparison_cumulative'),
        url(r'^charts\/senate-races\/(\w+)\/$','public_views.datapages.views.senate_races'),
        url(r'^charts\/$','public_views.datapages.views.chart_listing')

#        url(r'^race/(?P<cycle>\d\d\d\d)\/president\/', 'public_views.datapages.views.presidential_race'),

)
from django.conf.urls import patterns, url, include
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'new_filing', views.NFViewSet)
router.register(r'committee', views.COViewSet)
router.register(r'independent-expenditures', views.SkedEViewSet)
router.register(r'outside-spenders', views.OSViewSet)

#router.register(r'skededownloads', downloads.MyView)



urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
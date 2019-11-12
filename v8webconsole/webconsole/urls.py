from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.HostListView.as_view(), name='host_list'),
    url(r'^host/(?P<host_id>[0-9]+)/clusters/$', views.ClusterListView.as_view(), name='cluster_list'),
    url(r'^cluster/(?P<cluster_id>[0-9]+)/infobases/$', views.InfobaseListView.as_view(), name='infobase_list'),
]

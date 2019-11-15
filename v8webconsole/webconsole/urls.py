from django.urls import path
from .views import (
    HostsListView,
    HostAdminsListView,
    ClustersListView
)

urlpatterns = [
    path('hosts/', HostsListView.as_view(), name='hosts_list'),
    path('hosts/<int:id>/clusters/', ClustersListView.as_view(), name='clusters_list'),
    path('hosts/<int:id>/admins/', HostAdminsListView.as_view(), name='clusters_list'),
]

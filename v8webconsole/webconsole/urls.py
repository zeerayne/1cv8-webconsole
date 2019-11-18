from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostListView,
    HostAdminListView,
    ClusterListView,
)
from .views import InfobaseViewSet

router = DefaultRouter()
router.register(r'infobases', InfobaseViewSet, basename='infobase')

urlpatterns = [
    path('hosts/',
         HostListView.as_view(), name='hosts_list'),
    path('hosts/<int:host_id>/clusters/',
         ClusterListView.as_view(), name='clusters_list'),
    path('hosts/<int:host_id>/admins/',
         HostAdminListView.as_view(), name='cluster_admins_list'),
    path('hosts/<int:host_id>/clusters/<str:cluster_name>/',
         include(router.urls)),
]

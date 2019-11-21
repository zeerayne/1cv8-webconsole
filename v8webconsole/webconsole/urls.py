from django.urls import include
from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter
from .views import (
    HostViewSet,
    HostAdminViewSet,
    ClusterViewSet,
    InfobaseViewSet,
)

host_router = SimpleRouter()
host_router.register(r'hosts', HostViewSet, basename='host')

host_admin_router = NestedSimpleRouter(host_router, r'hosts', lookup='host')
host_admin_router.register(r'admins', HostAdminViewSet, basename='host-admin')

cluster_router = NestedSimpleRouter(host_router, r'hosts', lookup='host')
cluster_router.register(r'clusters', ClusterViewSet, basename='cluster')

infobase_router = NestedSimpleRouter(cluster_router, r'clusters', lookup='cluster')
infobase_router.register(r'infobases', InfobaseViewSet, basename='infobase')

urlpatterns = [
    url(r'^', include(host_router.urls)),
    url(r'^', include(host_admin_router.urls)),
    url(r'^', include(cluster_router.urls)),
    url(r'^', include(infobase_router.urls)),
]

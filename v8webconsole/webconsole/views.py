from django.views.generic import ListView
from v8webconsole.clusterconfig.models import Host, Cluster, ClusterCredentials
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import (generics, status)
from rest_framework.response import Response

from v8webconsole.core.cluster import ServerAgentControlInterface
from .views_mixins import GetRAgentInterfaceMixin
from .serializers import (
    HostSerializer,
    ClusterSerializer,
    RegUserSerializer,
    InfobaseSerializer,
)


class HostsListView(generics.ListAPIView):
    permission_classes = ()

    serializer_class = HostSerializer

    def get_queryset(self):
        return Host.objects.all()


class HostAdminsListView(GetRAgentInterfaceMixin, generics.GenericAPIView):
    permission_classes = ()

    serializer_class = RegUserSerializer

    def get_queryset(self):
        self.authenticate_agent()
        return self.get_ragent_interface().get_agent_admins()

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(data=qs, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClustersListView(GetRAgentInterfaceMixin, generics.GenericAPIView):
    permission_classes = ()

    serializer_class = ClusterSerializer

    def get_queryset(self):
        return self.get_ragent_interface().get_clusters()

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(data=qs, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)


class InfobaseListView(GetRAgentInterfaceMixin, generics.GenericAPIView):
    permission_classes = ()

    serializer_class = InfobaseSerializer

    def get_queryset(self):
        cluster = Cluster.objects.get(id=self.kwargs['cluster_id'])
        host = cluster.host
        cluster_credentials = ClusterCredentials.objects.filter(cluster__id=cluster.id)[:1].get()

        ragentci = ServerAgentControlInterface(host=host.address, port=host.port)
        clusterci = ragentci.get_cluster_interface(cluster.name)
        clusterci.cluster_auth(cluster_admin_name=cluster_credentials.login, cluster_admin_pwd=cluster_credentials.pwd)
        info_bases_short = clusterci.get_info_bases_short()
        return [ib.name for ib in info_bases_short]

from v8webconsole.clusterconfig.models import Host, Cluster, ClusterCredentials
from rest_framework import (generics, status, viewsets)
from rest_framework.response import Response

from .views_mixins import GetRAgentInterfaceMixin
from .serializers import (
    HostSerializer,
    ClusterSerializer,
    RegUserSerializer,
    ShortInfobaseSerializer,
    FullInfobaseSerializer,
)



class HostListView(generics.ListAPIView):
    permission_classes = ()

    serializer_class = HostSerializer

    def get_queryset(self):
        return Host.objects.all()


class HostAdminListView(GetRAgentInterfaceMixin, generics.GenericAPIView):
    permission_classes = ()

    serializer_class = RegUserSerializer

    def get_queryset(self):
        self.authenticate_agent()
        return self.get_ragent_interface().get_agent_admins()

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClusterListView(GetRAgentInterfaceMixin, generics.GenericAPIView):
    permission_classes = ()

    serializer_class = ClusterSerializer

    def get_queryset(self):
        return self.get_ragent_interface().get_clusters()

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InfobaseViewSet(GetRAgentInterfaceMixin, viewsets.GenericViewSet):
    short_serializer_class = ShortInfobaseSerializer
    full_serializer_class = FullInfobaseSerializer

    def get_queryset(self):
        self.authenticate_cluster_admin()
        return self.get_cluster_interface().get_info_bases_short()

    def get_object(self):
        self.authenticate_cluster_admin()
        self.get_cluster_interface().working_process_connection.add_authentication('Администратор', '')
        return next(filter(
            lambda ib: ib.name == self.kwargs['pk'],
            self.get_cluster_interface().working_process_connection.get_infobases()
        ))

    def list(self, request, **kwargs):
        qs = self.get_queryset()
        serializer = self.short_serializer_class(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        pass

    def retrieve(self, request, **kwargs):
        obj = self.get_object()
        serializer = self.full_serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

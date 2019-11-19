from v8webconsole.clusterconfig.models import (
    Host,
    Cluster,
    InfobaseCredentials,
    InfobaseDefaultCredentials,
)
from rest_framework import (
    generics,
    status,
    permissions,
    viewsets,
)
from rest_framework.response import Response

from .views_mixins import GetRAgentInterfaceMixin
from .serializers import (
    HostSerializer,
    ClusterSerializer,
    RegUserSerializer,
    ShortInfobaseSerializer,
    CreateInfobaseSerializer,
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

    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            return ShortInfobaseSerializer
        elif self.action == 'create':
            return CreateInfobaseSerializer
        else:
            return FullInfobaseSerializer

    def get_queryset(self):
        self.authenticate_cluster_admin()
        return self.get_cluster_interface().get_info_bases_short()

    def get_object(self):
        self.authenticate_cluster_admin()
        ib_name = self.kwargs['pk']
        cluster = Cluster.objects.get(name__iexact=self.kwargs['cluster_name'])
        try:
            ibc = InfobaseCredentials.objects.get(cluster=cluster, name__iexact=ib_name)
            self.get_cluster_interface().working_process_connection.add_authentication(ibc.login, ibc.pwd)
        except InfobaseCredentials.DoesNotExist:
            for ibc in InfobaseDefaultCredentials.objects.filter(cluster=cluster):
                self.get_cluster_interface().working_process_connection.add_authentication(ibc.login, ibc.pwd)
        return next(filter(
            lambda ib: ib.name == ib_name,
            self.get_cluster_interface().working_process_connection.get_infobases()
        ))

    def list(self, request, pk=None, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, pk=None, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        pass

    def partial_update(self, request, pk=None, **kwargs):
        pass

    def destroy(self, request, pk=None, **kwargs):
        pass

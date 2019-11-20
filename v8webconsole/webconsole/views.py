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
    UpdateInfobaseSerializer,
    DetailInfobaseSerializer,
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

    actions_map = {
        'list': ShortInfobaseSerializer,
        'create': CreateInfobaseSerializer,
        'update': UpdateInfobaseSerializer,
        'partial_update': UpdateInfobaseSerializer,
        'retrieve': DetailInfobaseSerializer,
    }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.actions_map.setdefault(self.action, DetailInfobaseSerializer)(*args, **kwargs)

    def get_detail_serializer(self, *args, **kwargs):
        return DetailInfobaseSerializer(*args, **kwargs)

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
        return self.get_cluster_interface().get_info_base(ib_name)

    def list(self, request, pk=None, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        detail_serializer = self.get_detail_serializer(instance)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save(cluster_interface=self.get_cluster_interface())

    def retrieve(self, request, pk=None, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        detail_serializer = self.get_detail_serializer(instance)
        return Response(detail_serializer.data)

    def perform_update(self, serializer):
        return serializer.save(cluster_interface=self.get_cluster_interface())

    def partial_update(self, request, pk=None, **kwargs):
        kwargs['partial'] = True
        return self.update(request, pk, **kwargs)

    def destroy(self, request, pk=None, **kwargs):
        pass

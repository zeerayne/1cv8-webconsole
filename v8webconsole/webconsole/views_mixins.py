from typing import Optional
from v8webconsole.clusterconfig.models import Host
from v8webconsole.core.cluster import (
    ServerAgentControlInterface,
    ClusterControlInterface,
)
from v8webconsole.clusterconfig.models import (
    Cluster,
)


class MultiSerializerViewSetMixin:
    """
    Примесь, которая позволяет переопределяя словарь actions_map управлять, какой сериализатор
    будет возвращен методом get_serializer
    """
    actions_map = {}

    default_serializer_class = None

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.actions_map.setdefault(self.action, self.default_serializer_class)(*args, **kwargs)

    def get_default_serializer_class(self):
        return self.default_serializer_class

    def get_default_serializer(self, *args, **kwargs):
        return self.get_default_serializer_class()(*args, **kwargs)


class RAgentInterfaceViewMixin:

    _ragent_interface: Optional[ServerAgentControlInterface]
    _cluster_interface: Optional[ClusterControlInterface]

    def get_ragent_interface(self) -> ServerAgentControlInterface:
        if not hasattr(self, '_ragent_interface'):
            host_id = self.kwargs['host_pk']
            self.__host = Host.objects.get(id=host_id)
            self._ragent_interface = ServerAgentControlInterface(host=self.__host.address, port=self.__host.port)
        return self._ragent_interface

    def authenticate_agent(self):
        ragent_interface = self.get_ragent_interface()
        credentials = self.__host.host_credentials.all()
        if len(credentials):
            creds = credentials[0]
            login, pwd = creds.login, creds.pwd
        else:
            login, pwd = '', ''
        ragent_interface.authenticate_agent(login, pwd)

    def get_cluster_model(self) -> Cluster:
        return Cluster.objects.get(name__iexact=self.kwargs['cluster_pk'])

    def get_cluster_interface(self) -> ClusterControlInterface:
        if not hasattr(self, '_cluster_interface'):
            self._cluster_interface = self.get_ragent_interface().get_cluster_interface(self.kwargs['cluster_pk'])
        return self._cluster_interface

    def authenticate_cluster_admin(self):
        cluster_interface = self.get_cluster_interface()
        if not cluster_interface.cluster_admin_authenticated:
            cluster = self.get_cluster_model()
            credentials = cluster.cluster_credentials.all()
            if len(credentials):
                creds = credentials[0]
                login, pwd = creds.login, creds.pwd
            else:
                login, pwd = '', ''
            cluster_interface.authenticate_cluster_admin(
                cluster_admin_name=login,
                cluster_admin_pwd=pwd
            )

    def authenticate_infobase_default_admin(self):
        cluster = self.get_cluster_model()
        credentials = cluster.infobase_default_credentials.all()
        for c in credentials:
            self.add_infobase_auth(c.login, c.pwd)

    def authenticate_infobase_admin(self, infobase_name):
        cluster = self.get_cluster_model()
        credentials = cluster.infobase_credentials.filter(name__iexact=infobase_name)
        if len(credentials):
            creds = credentials[0]
            login, pwd = creds.login, creds.pwd
            self.add_infobase_auth(login, pwd)
        else:
            self.authenticate_infobase_default_admin()

    def add_infobase_auth(self, login, password):
        self.get_cluster_interface().working_process_connection.add_authentication(login, password)

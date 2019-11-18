from typing import Optional
from v8webconsole.clusterconfig.models import Host
from v8webconsole.core.cluster import (
    ServerAgentControlInterface,
    ClusterControlInterface,
)
from v8webconsole.clusterconfig.models import (
    Cluster,
    ClusterCredentials,
)


class GetRAgentInterfaceMixin:

    _ragent_interface: Optional[ServerAgentControlInterface]
    _cluster_interface: Optional[ClusterControlInterface]

    def get_ragent_interface(self) -> ServerAgentControlInterface:
        if not hasattr(self, '_ragent_interface'):
            host_id = self.kwargs['host_id']
            self.__host = Host.objects.get(id=host_id)
            self._ragent_interface = ServerAgentControlInterface(host=self.__host.address, port=self.__host.port)
        return self._ragent_interface

    def authenticate_agent(self):
        ragent_interface = self.get_ragent_interface()
        credentials = self.__host.host_credentials.all()
        if len(credentials):
            creds = credentials[0]
            login, password = creds.login, creds.pwd
        else:
            login, password = '', ''
        ragent_interface.authenticate_agent(login, password)

    def get_cluster_interface(self) -> ClusterControlInterface:
        if not hasattr(self, '_cluster_interface'):
            self._cluster_interface = self.get_ragent_interface().get_cluster_interface(self.kwargs['cluster_name'])
        return self._cluster_interface

    def authenticate_cluster_admin(self):
        cluster_interface = self.get_cluster_interface()
        try:
            cluster = Cluster.objects.get(name=self.kwargs['cluster_name'])
            cluster_credentials = ClusterCredentials.objects.filter(cluster__id=cluster.id)[:1].get()
            login, pwd = cluster_credentials.login, cluster_credentials.pwd
        except Cluster.DoesNotExist:
            login, pwd = '', ''
        cluster_interface.authenticate_cluster_admin(
            cluster_admin_name=login,
            cluster_admin_pwd=pwd
        )

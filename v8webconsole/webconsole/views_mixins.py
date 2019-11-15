from typing import Optional
from v8webconsole.clusterconfig.models import Host
from v8webconsole.core.cluster import ServerAgentControlInterface


class GetRAgentInterfaceMixin:

    _ragent_interface: Optional[ServerAgentControlInterface]

    def get_ragent_interface(self) -> ServerAgentControlInterface:
        if not hasattr(self, '_ragent_interface'):
            host_id = self.kwargs['id']
            self.__host = Host.objects.get(id=host_id)
            self._ragent_interface = ServerAgentControlInterface(host=self.__host.address, port=self.__host.port)
        return self._ragent_interface

    def authenticate_agent(self):
        ragent = self.get_ragent_interface()
        credentials = self.__host.host_credentials.all()
        if len(credentials):
            creds = credentials[0]
            login, password = creds.login, creds.pwd
        else:
            login, password = '', ''
        ragent.authenticate_agent(login, password)

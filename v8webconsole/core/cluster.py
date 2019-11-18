import logging

"""
Для доступа к информационной базе из внешней программы используется COM объект COMConnector. 
В зависимости от версии платформы используется V82.COMConnector или V83.COMConnector. При установке платформы 1С, 
операционной системе автоматически регистрируется класс COMConnector. 
Если по каким либо причинам регистрация не прошла, то его можно зарегистрировать вручную.

Если COMConnector не зарегистрирован в Windows, то при программном создании объекта будет появляться ошибка:
> Ошибка при вызове конструктора (COMObject): -2147221164(0x80040154): Класс не зарегистрирован.

Для того чтобы зарегистрировать ComConnector в 64 разрядной операционной системе Windows выполняется
команда: regsvr32 "C:\\Program Files (x86)\\1cv8\\[version]\\bin\\comcntr.dll" 
"""
from typing import Tuple, List
from .comcntr import (
    COMConnector,
    ServerAgentConnection,
    WorkingProcessConnection,
    Cluster,
    InfobaseShort,
    Infobase,
)
from .exceptions import ClusterAdminAuthRequired


class ServerAgentControlInterface:

    def __init__(self, host: str, port: int = 1540):
        self.V8COMConnector = COMConnector()
        self.host = host
        self.agent_port = str(port)
        self.agent_connection = self.V8COMConnector.connect_agent(f'tcp://{host}:{port}')
        self.authenticated = False

    def authenticate_agent(self, login, password):
        self.agent_connection.authenticate_agent(login, password)
        self.authenticated = True

    def get_agent_admins(self):
        assert self.authenticated, 'Only authenticated user can use this method'
        return self.agent_connection.get_agent_admins()

    def get_cluster_interface(self, cluster_name: str) -> 'ClusterControlInterface':
        return ClusterControlInterface(self.host,
                                       self.V8COMConnector, self.agent_connection, self.get_cluster(cluster_name))

    def get_cluster_interfaces(self) -> List['ClusterControlInterface']:
        return [ClusterControlInterface(self.host, self.V8COMConnector, self.agent_connection, cluster)
                for cluster in self.get_clusters()]

    def get_clusters(self) -> List['Cluster']:
        return self.agent_connection.get_clusters()

    def get_cluster(self, cluster_name: str) -> 'Cluster':
        """
        Получает кластер из списка по его имени
        """
        for cluster in self.get_clusters():
            if cluster.cluster_name.lower() == cluster_name.lower():
                return cluster


class ClusterControlInterface:

    def __init__(self, host: str,
                 v8comconnector: 'COMConnector', agent_connection: 'ServerAgentConnection',  cluster: 'Cluster'):
        self.host = host  # TODO: это некорректно, необходимо придумать способ лучше
        self.V8COMConnector = v8comconnector
        self.agent_connection = agent_connection
        self.cluster = cluster
        self.cluster_admin_name = None
        self.cluster_admin_pwd = None
        self.__cluster_auth_passed = False
        self.__working_process_connection = None

    def authenticate_cluster_admin(self, cluster_admin_name: str, cluster_admin_pwd: str):
        """
        Авторизует соединение с агентом сервера для указанного кластера.
        :param cluster_admin_name: Имя администратора кластера
        :param cluster_admin_pwd: Пароль администраотра кластера
        """
        self.agent_connection.authenticate(self.cluster, cluster_admin_name, cluster_admin_pwd)
        self.cluster_admin_name, self.cluster_admin_pwd = cluster_admin_name, cluster_admin_pwd
        self.__cluster_auth_passed = True

    def __check_cluster_auth(self):
        if not self.__cluster_auth_passed:
            raise ClusterAdminAuthRequired('Cluster admin auth required')

    @property
    def working_process_connection(self) -> 'WorkingProcessConnection':
        if self.__working_process_connection:
            return self.__working_process_connection
        self.__check_cluster_auth()
        working_process = None
        for wp in self.agent_connection.get_working_processes(self.cluster):
            if wp.running == 1:
                working_process = wp
                break
        # TODO: корректнее будет использовать working_process.hostname, но есть ньюансы
        working_process_host = self.host
        working_process_port = str(working_process.main_port)
        working_process_connection = self.V8COMConnector.connect_working_process(
            f'tcp://{working_process_host}:{working_process_port}'
        )
        # Выполняет аутентификацию администратора кластера.
        # Администратор кластера должен быть аутентифицирован для создания в этом кластере новой информационной базы.
        working_process_connection.authenticate_admin(self.cluster_admin_name, self.cluster_admin_pwd)
        self.__working_process_connection = working_process_connection
        return self.__working_process_connection

    def add_infobase_auth(self, login, password):
        """
        Добавляет аутентификацию для информационной базы. Имя информационной базы не требуется т.к. аутентификаия будет
        выполнена во всех базах, к которым подходит переданная пара логин/пароль
        :param login:
        :param password:
        """
        working_process_connection = self.working_process_connection
        # Административный доступ разрешен только к тем информационным базам,
        # в которых зарегистрирован пользователь с таким именем и он имеет право "Администратор".
        working_process_connection.add_authentication(login, password)

    def get_info_bases(self) -> List['Infobase']:
        """
        Получает список информационных баз в кластере
        Для чтения значений всех их свойств, кроме Name, необходимы административные права.
        """
        return self.working_process_connection.get_infobases()

    def get_info_bases_short(self) -> List['InfobaseShort']:
        """
        Получает список кратких описаний информационных баз в кластере.
        Для успешного выполнения метода необходима аутентификация одного из администраторов кластера.
        """
        self.__check_cluster_auth()
        return self.agent_connection.get_infobases(self.cluster)

    def get_info_base_metadata(self, info_base, info_base_user, info_base_pwd) -> Tuple[str, str]:
        """
        Получает наименование и версию конфигурации
        :param info_base: Имя информационной базы
        :param info_base_user: Пользователь ИБ с правами администратора
        :param info_base_pwd: Пароль пользователя ИБ
        :return: tuple(Наименование, Версия информационной базы)
        """
        external_connection = self.V8COMConnector.connect(
            f'Srvr="{self.host}";Ref="{info_base}";Usr="{info_base_user}";Pwd="{info_base_pwd}";'
        )
        version = external_connection.Metadata.Version
        name = external_connection.Metadata.Name
        del external_connection
        return name, version

    def lock_info_base(self, info_base: 'Infobase', permission_code='0000', message='Выполняется обслуживание ИБ'):
        """
        Блокирует фоновые задания и новые сеансы информационной базы
        :param info_base:
        :param permission_code: Код доступа к информационной базе во время блокировки сеансов
        :param message: Сообщение будет выводиться при попытке установить сеанс с ИБ
        """
        # TODO: необходима проверка, есть ли у рабочего процесса необходимые авторизационные данные для этой ИБ
        info_base.ScheduledJobsDenied = True
        info_base.SessionsDenied = True
        info_base.PermissionCode = permission_code
        info_base.DeniedMessage = message
        self.working_process_connection.update_infobase(info_base)
        logging.debug(f'[{info_base.name}] Lock info base successfully')

    def unlock_info_base(self, info_base: 'Infobase'):
        """
        Снимает блокировку фоновых заданий и сеансов информационной базы
        """
        info_base.ScheduledJobsDenied = False
        info_base.SessionsDenied = False
        info_base.DeniedMessage = ""
        self.working_process_connection.update_infobase(info_base)
        logging.debug(f'[{info_base.name}] Unlock info base successfully')

    def terminate_info_base_sessions(self, info_base_short: 'InfobaseShort'):
        """
        Принудительно завершает текущие сеансы информационной базы
        :param info_base_short: краткое описание информационной базы
        """
        info_base_sessions = self.agent_connection.get_infobase_sessions(self.cluster, info_base_short)
        for session in info_base_sessions:
            self.agent_connection.terminate_session(self.cluster, session)

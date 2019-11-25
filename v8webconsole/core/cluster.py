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
    RegUser,
)
from .exceptions import ClusterAdminAuthRequired


class ServerAgentControlInterface:

    def __init__(self, host: str, port: int = 1540):
        self.V8COMConnector = COMConnector()
        self.host = host
        self.agent_port = str(port)
        self.agent_connection = self.V8COMConnector.connect_agent(f'tcp://{host}:{port}')
        self.__authenticated = False

    def authenticate_agent(self, login, password):
        self.agent_connection.authenticate_agent(login, password)
        self.__authenticated = True

    def get_agent_admins(self) -> List['RegUser']:
        """
        Получает список администраторов центрального сервера.
        Для получения списка требуется аутентификация одного из администраторов
        """
        assert self.__authenticated, 'Only authenticated user can use this method. ' \
                                     'Authenticate using "authenticate_agent" method'
        return self.agent_connection.get_agent_admins()

    def get_agent_admin(self, name) -> 'RegUser':
        return next(filter(
            lambda admin: admin.name.lower() == name.lower(),
            self.get_agent_admins()
        ))

    def get_cluster_interface(self, cluster_name: str) -> 'ClusterControlInterface':
        return ClusterControlInterface(self.host,
                                       self.V8COMConnector, self.agent_connection, self.get_cluster(cluster_name))

    def get_cluster_interfaces(self) -> List['ClusterControlInterface']:
        return [ClusterControlInterface(self.host, self.V8COMConnector, self.agent_connection, cluster)
                for cluster in self.get_clusters()]

    def get_clusters(self) -> List['Cluster']:
        """
        Получает список кластеров
        """
        return self.agent_connection.get_clusters()

    def get_cluster(self, cluster_name: str) -> 'Cluster':
        """
        Получает кластер по его имени
        """
        return next(filter(
            lambda cluster: cluster.cluster_name.lower() == cluster_name.lower(),
            self.get_clusters()
        ))

    def reg_cluster(self, cluster: 'Cluster'):
        self.agent_connection.reg_cluster(cluster)

    def unreg_cluster(self, cluster: 'Cluster', login, pwd):
        """
        Выполняет отмену регистрации кластера. Для успешного выполнения метода необходима аутентификация одного из
        администраторов кластера. Возможна отмена регистрации только пустого кластера.
        :param cluster: кластер
        :param login: логин администратора кластера
        :param pwd: пароль администратора кластера
        """
        self.agent_connection.authenticate(cluster, login, pwd)
        self.agent_connection.unreg_cluster(cluster)


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
    def cluster_admin_authenticated(self):
        return self.__cluster_auth_passed

    @property
    def working_process_connection(self) -> 'WorkingProcessConnection':
        if self.__working_process_connection:
            return self.__working_process_connection
        self.__check_cluster_auth()
        working_process = next(filter(
            lambda wp: wp.running == 1,
            self.agent_connection.get_working_processes(self.cluster)
        ))
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

    def get_infobases(self) -> List['Infobase']:
        """
        Получает список информационных баз в кластере
        Для чтения значений всех их свойств, кроме Name, необходимы административные права.
        """
        return self.working_process_connection.get_infobases()

    def get_infobase(self, name) -> 'Infobase':
        """
        Получает информационную базу по имени
        Для чтения значений всех их свойств, кроме Name, необходимы административные права.
        """
        return next(filter(lambda ib: name.lower() == ib.name.lower(), self.get_infobases()))

    def get_infobases_short(self) -> List['InfobaseShort']:
        """
        Получает список кратких описаний информационных баз в кластере.
        Для успешного выполнения метода необходима аутентификация одного из администраторов кластера.
        """
        self.__check_cluster_auth()
        return self.agent_connection.get_infobases(self.cluster)

    def get_infobase_metadata(self, infobase, infobase_user, infobase_pwd) -> Tuple[str, str]:
        """
        Получает наименование и версию конфигурации
        :param infobase: Имя информационной базы
        :param infobase_user: Пользователь ИБ с правами администратора
        :param infobase_pwd: Пароль пользователя ИБ
        :return: tuple(Наименование, Версия информационной базы)
        """
        external_connection = self.V8COMConnector.connect(
            f'Srvr="{self.host}";Ref="{infobase}";Usr="{infobase_user}";Pwd="{infobase_pwd}";'
        )
        version = external_connection.Metadata.Version
        name = external_connection.Metadata.Name
        del external_connection
        return name, version

    def lock_infobase(self, infobase: 'Infobase', permission_code='0000', message='Выполняется обслуживание ИБ'):
        """
        Блокирует фоновые задания и новые сеансы информационной базы
        :param infobase:
        :param permission_code: Код доступа к информационной базе во время блокировки сеансов
        :param message: Сообщение будет выводиться при попытке установить сеанс с ИБ
        """
        # TODO: необходима проверка, есть ли у рабочего процесса необходимые авторизационные данные для этой ИБ
        infobase.scheduled_jobs_denied = True
        infobase.sessions_denied = True
        infobase.permission_code = permission_code
        infobase.denied_message = message
        self.working_process_connection.update_infobase(infobase)
        logging.debug(f'[{infobase.name}] Lock info base successfully')

    def set_recycling_by_memory(self, max_memory_size: int, duration: int):
        self.agent_connection.set_cluster_recycling_by_memory(self.cluster, max_memory_size, duration)

    def set_recycling_by_time(self, lifetime_limit: int):
        self.agent_connection.set_cluster_recycling_by_time(self.cluster, lifetime_limit)

    def set_recycling_errors_count_threshold(self, errors_count_threshold: int):
        self.agent_connection.set_cluster_recycling_errors_count_threshold(self.cluster, errors_count_threshold)

    def set_recycling_expiration_timeout(self, expiration_timeout: int):
        self.agent_connection.set_cluster_recycling_expiration_timeout(self.cluster, expiration_timeout)

    def set_recycling_kill_problem_processes(self, kill_problem_processes: bool):
        self.agent_connection.set_cluster_recycling_kill_problem_processes(self.cluster, kill_problem_processes)

    def set_security_level(self, security_level: int):
        self.agent_connection.set_cluster_security_level(self.cluster, security_level)

    def unlock_infobase(self, infobase: 'Infobase'):
        """
        Снимает блокировку фоновых заданий и сеансов информационной базы
        """
        infobase.ScheduledJobsDenied = False
        infobase.SessionsDenied = False
        infobase.DeniedMessage = ""
        self.working_process_connection.update_infobase(infobase)
        logging.debug(f'[{infobase.name}] Unlock info base successfully')

    def terminate_info_base_sessions(self, infobase_short: 'InfobaseShort'):
        """
        Принудительно завершает текущие сеансы информационной базы
        :param infobase_short: краткое описание информационной базы
        """
        info_base_sessions = self.agent_connection.get_infobase_sessions(self.cluster, infobase_short)
        for session in info_base_sessions:
            self.agent_connection.terminate_session(self.cluster, session)

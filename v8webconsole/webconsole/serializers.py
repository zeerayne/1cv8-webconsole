from rest_framework import serializers


SECURITY_LEVEL_CHOICES = [(0, 'no_encryption'), (1, 'encrypted_auth'), (2, 'encrypted_always'), ]


class HostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    address = serializers.CharField()
    port = serializers.IntegerField()


class RegUserSerializer(serializers.Serializer):
    name = serializers.CharField()


class ShortClusterSerializer(serializers.Serializer):
    cluster_name = serializers.CharField()


class DetailClusterSerializer(ShortClusterSerializer):
    errors_count_threshold = serializers.IntegerField(
        required=False,
    )
    expiration_timeout = serializers.IntegerField(
        required=False,
    )
    hostname = serializers.CharField(
        required=False,
    )
    kill_problem_processes = serializers.BooleanField(
        required=False,
    )
    lifetime_limit = serializers.IntegerField(
        required=False,
    )
    load_balancing_mode = serializers.ChoiceField(
        choices=[(0, 'performance'), (1, 'memory'), ],
        required=False,
    )
    main_port = serializers.IntegerField(
        required=False,
    )
    max_memory_size = serializers.IntegerField(
        required=False,
    )
    max_memory_time_limit = serializers.IntegerField(
        required=False,
    )
    security_level = serializers.ChoiceField(
        choices=SECURITY_LEVEL_CHOICES,
        required=False,
    )
    session_fault_tolerance_level = serializers.IntegerField(
        required=False,
    )

    def create(self, validated_data):
        ragent_interface = validated_data.pop('ragent_interface')
        cluster = ragent_interface.agent_connection.create_cluster_info()
        for key, value in validated_data.items():
            setattr(cluster, key, value)
        ragent_interface.reg_cluster(cluster)
        return ragent_interface.get_cluster(cluster.name)

    def update(self, instance, validated_data):
        ragent_interface = validated_data.pop('ragent_interface')
        cluster_interface = validated_data.pop('cluster_interface')
        cluster = self.instance
        if 'max_memory_size' in validated_data and 'max_memory_time_limit' in validated_data:
            max_memory_size = validated_data['max_memory_size']
            max_memory_time_limit = validated_data['max_memory_time_limit']
            if max_memory_size != cluster.max_memory_size or max_memory_time_limit != cluster.max_memory_time_limit:
                cluster_interface.set_recycling_by_memory(
                    max_memory_size,
                    max_memory_time_limit
                )
        if 'lifetime_limit' in validated_data:
            lifetime_limit = validated_data['lifetime_limit']
            if lifetime_limit != cluster.lifetime_limit:
                cluster_interface.set_recycling_by_time(
                    lifetime_limit
                )
        if 'errors_count_threshold' in validated_data:
            errors_count_threshold = validated_data['errors_count_threshold']
            if errors_count_threshold != cluster.errors_count_threshold:
                cluster_interface.set_recycling_errors_count_threshold(
                    errors_count_threshold
                )
        if 'expiration_timeout' in validated_data:
            expiration_timeout = validated_data['expiration_timeout']
            if expiration_timeout != cluster.expiration_timeout:
                cluster_interface.set_recycling_expiration_timeout(
                    expiration_timeout
                )
        if 'kill_problem_processes' in validated_data:
            kill_problem_processes = validated_data['kill_problem_processes']
            if kill_problem_processes != cluster.kill_problem_processes:
                cluster_interface.set_recycling_kill_problem_processes(
                    kill_problem_processes
                )
        if 'security_level' in validated_data:
            security_level = validated_data['security_level']
            if security_level != cluster.security_level:
                cluster_interface.set_security_level(
                    security_level
                )
        return ragent_interface.get_cluster(cluster.name)


class ShortInfobaseSerializer(serializers.Serializer):
    name = serializers.CharField()
    descr = serializers.CharField(
        required=False,
    )


class UpdateInfobaseSerializer(serializers.Serializer):
    descr = serializers.CharField(
        required=False,
    )
    dbms = serializers.CharField(
        required=False,
    )
    db_name = serializers.CharField(
        required=False,
    )
    db_password = serializers.CharField(
        write_only=True,
        required=False,
    )
    db_server_name = serializers.CharField(
        required=False,
    )
    db_user = serializers.CharField(
        required=False,
    )
    denied_from = serializers.DateTimeField(
        required=False,
    )
    denied_to = serializers.DateTimeField(
        required=False,
    )
    denied_message = serializers.CharField(
        required=False,
    )
    denied_parameter = serializers.CharField(
        required=False,
    )
    external_session_manager_connection_string = serializers.CharField(
        required=False,
    )
    external_session_manager_required = serializers.BooleanField(
        required=False,
    )
    license_distribution_allowed = serializers.BooleanField(
        required=False,
    )
    permission_code = serializers.CharField(
        required=False,
    )
    safe_mode_security_profile_name = serializers.CharField(
        required=False,
    )
    scheduled_jobs_denied = serializers.BooleanField(
        required=False,
    )
    security_level = serializers.ChoiceField(
        choices=SECURITY_LEVEL_CHOICES,
        required=False,
    )
    security_profile_name = serializers.CharField(
        required=False,
    )
    sessions_denied = serializers.BooleanField(
        required=False,
    )

    def save(self, **kwargs):
        cluster_interface = kwargs['cluster_interface']
        infobase = self.instance
        for key, value in self.validated_data.items():
            setattr(infobase, key, value)
        cluster_interface.working_process_connection.update_infobase(infobase)
        infobase = cluster_interface.get_infobase(infobase.name)
        return infobase


class CreateInfobaseSerializer(ShortInfobaseSerializer):
    date_offset = serializers.IntegerField(
        write_only=True,
        required=False,
    )
    dbms = serializers.CharField()
    db_name = serializers.CharField()
    db_password = serializers.CharField(
        write_only=True,
    )
    db_server_name = serializers.CharField()
    db_user = serializers.CharField()
    license_distribution_allowed = serializers.BooleanField()
    locale = serializers.CharField(
        write_only=True,
    )
    scheduled_jobs_denied = serializers.BooleanField()
    create_db = serializers.BooleanField(
        required=False,
    )

    def save(self, **kwargs):
        cluster_interface = kwargs['cluster_interface']
        create_db = self.validated_data.pop('create_db', False)
        infobase = cluster_interface.working_process_connection.create_infobase_info()
        for key, value in self.validated_data.items():
            setattr(infobase, key, value)
        cluster_interface.working_process_connection.create_infobase(infobase, create_db)
        infobase = cluster_interface.get_infobase(self.validated_data['name'])
        return infobase


class DetailInfobaseSerializer(ShortInfobaseSerializer):
    date_offset = serializers.IntegerField(
        write_only=True,
    )
    dbms = serializers.CharField()
    db_name = serializers.CharField()
    db_password = serializers.CharField(
        write_only=True,
    )
    db_server_name = serializers.CharField()
    db_user = serializers.CharField()
    denied_from = serializers.DateTimeField()
    denied_to = serializers.DateTimeField()
    denied_message = serializers.CharField()
    denied_parameter = serializers.CharField()
    external_session_manager_connection_string = serializers.CharField()
    external_session_manager_required = serializers.BooleanField()
    license_distribution_allowed = serializers.BooleanField()
    locale = serializers.CharField(
        write_only=True,
    )
    permission_code = serializers.CharField()
    safe_mode_security_profile_name = serializers.CharField()
    scheduled_jobs_denied = serializers.BooleanField()
    security_level = serializers.ChoiceField(
        choices=SECURITY_LEVEL_CHOICES,
    )
    security_profile_name = serializers.CharField()
    sessions_denied = serializers.BooleanField()

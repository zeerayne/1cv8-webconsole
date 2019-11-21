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
    life_time_limit = serializers.IntegerField(
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
        infobase = cluster_interface.get_info_base(infobase.name)
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
        infobase = cluster_interface.get_info_base(self.validated_data['name'])
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

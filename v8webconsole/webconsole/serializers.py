from rest_framework import serializers


class HostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    address = serializers.CharField()
    port = serializers.IntegerField()


class RegUserSerializer(serializers.Serializer):
    name = serializers.CharField()


class ClusterSerializer(serializers.Serializer):
    cluster_name = serializers.CharField()


class ShortInfobaseSerializer(serializers.Serializer):
    name = serializers.CharField()
    descr = serializers.CharField()


class FullInfobaseSerializer(ShortInfobaseSerializer):
    date_offset = serializers.IntegerField(write_only=True)
    dbms = serializers.CharField()
    db_name = serializers.CharField()
    db_password = serializers.CharField(write_only=True)
    db_server_name = serializers.CharField()
    db_user = serializers.CharField()
    denied_from = serializers.DateTimeField()
    denied_to = serializers.DateTimeField()
    denied_message = serializers.CharField()
    denied_parameter = serializers.CharField()
    external_session_manager_connection_string = serializers.CharField()
    external_session_manager_required = serializers.BooleanField()
    license_distribution_allowed = serializers.BooleanField()
    locale = serializers.CharField(write_only=True)
    permission_code = serializers.CharField()
    safe_mode_security_profile_name = serializers.CharField()
    scheduled_jobs_denied = serializers.BooleanField()
    security_level = serializers.IntegerField()
    security_profile_name = serializers.CharField()
    sessions_denied = serializers.BooleanField()

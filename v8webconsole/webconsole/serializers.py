from rest_framework import serializers


class HostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    address = serializers.CharField()
    port = serializers.IntegerField()


class RegUserSerializer(serializers.Serializer):
    name = serializers.CharField()


class ClusterSerializer(serializers.Serializer):
    cluster_name = serializers.CharField()


class InfobaseSerializer(serializers.Serializer):
    name = serializers.CharField()

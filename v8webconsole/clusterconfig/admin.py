from django.contrib import admin
from .models import (
    Host,
    HostCredentials,
    Cluster,
    ClusterCredentials,
    InfobaseCredentials
)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('address', 'port', )

    def client_name(self, obj):
        return obj.client.name
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'client__name'


@admin.register(HostCredentials)
class HostCredentialsAdmin(admin.ModelAdmin):
    list_display = ('login', 'host', )

    def host(self, obj):
        host = obj.host
        return f'{host.address}:{host.port}'
    host.short_description = 'Host'
    host.admin_order_field = 'host__name'


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', )

    def host(self, obj):
        host = obj.host
        return f'{host.address}:{host.port}'
    host.short_description = 'Host'
    host.admin_order_field = 'host__name'


@admin.register(ClusterCredentials)
class ClusterCredentialsAdmin(admin.ModelAdmin):
    list_display = ('login', 'cluster', 'host', )

    def cluster(self, obj):
        cluster = obj.cluster
        return f'{cluster.name}'
    cluster.short_description = 'Cluster'
    cluster.admin_order_field = 'cluster__name'

    def host(self, obj):
        host = obj.cluster.host
        return f'{host.address}:{host.port}'
    host.short_description = 'Host'
    host.admin_order_field = 'cluster__host__name'


@admin.register(InfobaseCredentials)
class InfobaseCredentialsAdmin(admin.ModelAdmin):
    list_display = ('name', 'login', 'cluster', 'host',)

    def cluster(self, obj):
        cluster = obj.cluster
        return f'{cluster.name}'

    cluster.short_description = 'Cluster'
    cluster.admin_order_field = 'cluster__name'

    def host(self, obj):
        host = obj.cluster.host
        return f'{host.address}:{host.port}'

    host.short_description = 'Host'
    host.admin_order_field = 'cluster__host__name'

from django.views.generic import ListView
from v8webconsole.clusterconfig.models import Host, Cluster, ClusterCredentials
from django.db import models
from django.db.models.fields import reverse_related, related
from django.contrib.auth.mixins import LoginRequiredMixin
from v8webconsole.core import cluster as core_cluster


def get_field_names(model_class):
    return [field.name for field in model_class._meta.get_fields()
            if not isinstance(field, (models.AutoField, reverse_related.ForeignObjectRel, related.RelatedField))
            ]


class HostListView(LoginRequiredMixin, ListView):
    model = Host
    template_name = 'host_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['field_names'] = get_field_names(self.model)
        return ctx


class ClusterListView(LoginRequiredMixin, ListView):
    model = Cluster
    template_name = 'cluster_list.html'

    def get_queryset(self):
        return self.model.objects.filter(host__id=self.kwargs['host_id'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['field_names'] = get_field_names(self.model)
        return ctx


class InfobaseListView(LoginRequiredMixin, ListView):
    template_name = 'infobase_list.html'

    def get_queryset(self):
        cluster = Cluster.objects.get(id=self.kwargs['cluster_id'])
        host = cluster.host
        cluster_credentials = ClusterCredentials.objects.filter(cluster__id=cluster.id)[:1].get()

        ragentci = core_cluster.ServerAgentControlInterface(host=host.address, port=host.port)
        clusterci = ragentci.get_cluster_interface(cluster.name)
        clusterci.cluster_auth(cluster_admin_name=cluster_credentials.login, cluster_admin_pwd=cluster_credentials.pwd)
        info_bases_short = clusterci.get_info_bases_short()
        return [ib.name for ib in info_bases_short]

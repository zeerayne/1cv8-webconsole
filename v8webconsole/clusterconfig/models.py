from django.db import models


class Host(models.Model):
    address = models.CharField(max_length=100)
    port = models.IntegerField()

    def __str__(self):
        return f'{self.address}:{self.port}'


class HostCredentials(models.Model):
    class Meta:
        verbose_name_plural = "Host credentials"

    login = models.CharField(max_length=100)
    pwd = models.CharField(max_length=100, blank=True)
    host = models.ForeignKey(to=Host, on_delete=models.CASCADE, related_name='host_credentials')

    def __str__(self):
        return f'{self.login} on host {self.host}'


class Cluster(models.Model):
    name = models.CharField(max_length=100)
    host = models.ForeignKey(to=Host, on_delete=models.CASCADE, related_name='clusters')

    def __str__(self):
        return f'{self.name} on host {self.host}'


class ClusterCredentials(models.Model):
    class Meta:
        verbose_name_plural = "Cluster credentials"

    login = models.CharField(max_length=100)
    pwd = models.CharField(max_length=100, blank=True)
    cluster = models.ForeignKey(to=Cluster, on_delete=models.CASCADE, related_name='cluster_credentials')

    def __str__(self):
        return f'{self.login} in cluster {self.cluster}'


class InfobaseCredentials(models.Model):
    class Meta:
        verbose_name_plural = "Infobase credentials"

    name = models.CharField(max_length=100)
    login = models.CharField(max_length=100, blank=True)
    pwd = models.CharField(max_length=100, blank=True)
    cluster = models.ForeignKey(to=Cluster, on_delete=models.CASCADE, related_name='infobase_credentials')

    def __str__(self):
        return f'{self.name} in cluster {self.cluster}'

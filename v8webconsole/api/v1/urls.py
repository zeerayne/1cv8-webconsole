from django.urls import path
from django.conf.urls import include

urlpatterns = [
    path('webconsole/', include('v8webconsole.webconsole.urls')),
]

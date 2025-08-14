from django.urls import path, include
from dgpf_scopetest import views

urlpatterns = [
    path("", views.index, name="index"),
    path("transfer/", views.transfer, name="transfer"),
    path("transfers/", views.view_transfers, name="transfers"),
    path("flows/", views.view_flows, name="flows"),
    path("flow/start/", views.flow_start, name="flow-start"),
    path("flow/create/", views.flow_create, name="flow-create"),
    # Provides the basic search portal
    path("search/", include("globus_portal_framework.urls")),
    # Provides Login urls for Globus Auth
    path("", include("social_django.urls", namespace="social")),
]

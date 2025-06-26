from django.urls import path, include
from dgpf_scopetest import views

urlpatterns = [
    path("", views.index, name="index"),
    path("transfer", views.transfer, name="transfer"),
    # Provides the basic search portal
    path("search/", include("globus_portal_framework.urls")),
    # Provides Login urls for Globus Auth
    path("", include("social_django.urls", namespace="social")),
]

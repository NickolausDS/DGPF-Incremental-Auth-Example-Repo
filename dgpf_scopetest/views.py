import logging
from urllib.parse import urlparse
import globus_sdk
import django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from globus_portal_framework.apps import get_setting
from globus_portal_framework import (
    gsearch,
    gclients,
    gtransfer,
    PreviewException,
    PreviewURLNotFound,
    ExpiredGlobusToken,
    GroupsException,
)
from dgpf_scopetest import forms

log = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    user_data = {}
    if request.user.is_authenticated:
        user_data = request.user.social_auth.get(provider="globus").extra_data

    return render(request, "index.html", user_data)


def transfer(request: HttpRequest) -> HttpResponse:
    form = forms.TransferForm(request.GET or None)

    if request.POST and form.is_valid():
        # You could actually save through AJAX and return a success code here
        transfer_client = gclients.load_transfer_client(request.user)
        tdata = globus_sdk.TransferData(
            transfer_client,
            # Globus Tutorial Collection 1
            "6c54cade-bde5-45c1-bdea-f4bd71dba2cc",
            form.endpoint_id,
            label="SDK example",
            sync_level="checksum",
        )
        tdata.add_item("/home/share/godata/", form.path, recursive=True)
        transfer_result = transfer_client.submit_transfer(tdata)
        log.info("Transfer Started!")

    return render(request, "transfer.html", {"form": form})

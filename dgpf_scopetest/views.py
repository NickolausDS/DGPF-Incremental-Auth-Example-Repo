import logging
import globus_sdk
import json
import globus_sdk.scopes
import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.conf import settings

from globus_portal_framework.exc import ScopesRequired
from globus_portal_framework.decorators import scopes_required
from globus_portal_framework.gclients import (
    load_transfer_client,
    load_globus_client,
    load_scopes,
    load_specific_flow_client,
)
import dgpf_scopetest.utils

log = logging.getLogger(__name__)

TRANSFER_SCOPE = globus_sdk.TransferClient.scopes.all
TUTORIAL_ENDPOINT_SCOPE = globus_sdk.scopes.GCSCollectionScopes(
    settings.SOURCE_ENDPOINT
).data_access
TRANSFER_SCOPE.with_dependency(TUTORIAL_ENDPOINT_SCOPE)


def index(request: HttpRequest) -> HttpResponse:
    """
    Show all of the current scopes a user has logged in with.
    """
    user_data = {}
    if request.user.is_authenticated:
        user_data = request.user.social_auth.get(provider="globus").extra_data

    return render(request, "index.html", user_data)


@scopes_required([globus_sdk.TransferClient.scopes.all])
def transfer(request: HttpRequest) -> HttpResponse:
    transfer_client = load_transfer_client(request.user)
    form = dgpf_scopetest.utils.get_transfer_form(request)

    if request.POST and form.is_valid():
        tdata = globus_sdk.TransferData(
            settings.SOURCE_ENDPOINT,
            form.cleaned_data["endpoint_id"],
            label=form.cleaned_data.get("label", "My Transfer"),
            sync_level="checksum",
        )
        log.debug(form.cleaned_data)
        tdata.add_item("/home/share/godata/", form.cleaned_data["path"], recursive=True)
        transfer_result = transfer_client.submit_transfer(tdata)
        messages.info(request, "Transfer Started!")
        return redirect("transfers")

    return render(request, "transfer.html", {"form": form})


def view_transfers(request: HttpRequest) -> HttpResponse:
    tc = load_transfer_client(request.user)
    transfers = tc.task_list(limit=10, orderby="request_time DESC").data["DATA"]

    for transfer in transfers:
        transfer["request_time"] = datetime.datetime.fromisoformat(
            transfer["request_time"]
        )
        if transfer["completion_time"]:
            transfer["completion_time"] = datetime.datetime.fromisoformat(
                transfer["completion_time"]
            )
    return render(request, "transfers.html", {"transfers": transfers})


def view_flows(request: HttpRequest) -> HttpResponse:
    fc = load_globus_client(
        request.user, globus_sdk.FlowsClient, require_authorized=True
    )
    flows = fc.list_flows(orderby="created_at DESC").data["flows"]
    flows = [
        f
        for f in flows
        if len(f["definition"]["States"]) == 1
        and f["definition"]["States"].get("GlobusTransfer")
    ]
    for flow in flows:
        flow["created_at"] = datetime.datetime.fromisoformat(flow["created_at"])
        flow["selected"] = flow["id"] == request.session.get("selected_flow", {}).get(
            "id"
        )
    return render(request, "flows.html", {"flows": flows})


def flow_create(request: HttpRequest) -> HttpResponse:
    fc = load_globus_client(
        request.user, globus_sdk.FlowsClient, require_authorized=True
    )
    definition = json.loads(settings.TRANSFER_FLOW_DEFINITION_FILENAME.read_text())
    flow = fc.create_flow(
        "Scopetest Transfer",
        definition,
        {},
        subtitle="None",
        description="A flow for scope testing",
        flow_starters=["all_authenticated_users"],
        keywords=["gloubs", "scope", "test"],
    )
    request.session["selected_flow"] = {"id": flow["id"], "title": flow["title"]}
    messages.info(request, "Your new flow has been created!")
    return redirect("flows")


def flow_start(request: HttpRequest) -> HttpResponse:
    """
    Start the specified flow. Login if needed
    """
    selected_flow = dgpf_scopetest.utils.get_selected_flow(request)
    flow_id = selected_flow.get("id")
    if not flow_id:
        messages.error(request, "You need to select a flow.")
        return redirect("flows")

    sfc = load_specific_flow_client(request.user, flow_id)
    form = dgpf_scopetest.utils.get_transfer_form(request)

    if request.POST and form.is_valid():
        globus_user_uuid = request.user.social_auth.get(provider="globus").uid
        sfc.run_flow(
            {
                "input": {
                    "transfer_source_endpoint_id": settings.SOURCE_ENDPOINT,
                    "transfer_source_path": "/home/share/godata/",
                    "transfer_destination_endpoint_id": form.cleaned_data[
                        "endpoint_id"
                    ],
                    "transfer_destination_path": form.cleaned_data["path"],
                    "transfer_recursive": True,
                }
            },
            label=f"Transfer for {request.user.username}",
            tags=["test", "globus", "scopes"],
            run_monitors=[f"urn:globus:auth:identity:{globus_user_uuid}"],
        )
        messages.info(request, "Flow started!")
        return redirect("flows")

    return render(request, "flow-start.html", {"form": form})

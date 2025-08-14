import logging
from django.http import HttpRequest
import dgpf_scopetest.forms

log = logging.getLogger(__name__)


def get_transfer_form(request: HttpRequest) -> dgpf_scopetest.forms.TransferForm:
    # Cache selected endpoint between requests
    if request.POST.get("endpoint_id"):
        form = dgpf_scopetest.forms.TransferForm(request.POST)
        request.session["cached_transfer"] = request.POST
        log.debug("Caching POST Request")
    elif request.GET.get("endpoint_id"):
        form = dgpf_scopetest.forms.TransferForm(request.GET)
        request.session["cached_transfer"] = request.GET
        log.debug("Caching GET Request")
    else:
        form = dgpf_scopetest.forms.TransferForm(request.session.get("cached_transfer"))

    return form


def get_selected_flow(request):
    if request.GET.get("flow_id"):
        set_selected_flow(request, request.GET["flow_id"], request.GET.get("title"))
    return request.session.get("selected_flow", {})


def set_selected_flow(request, flow_id, title):
    request.session["selected_flow"] = dict(flow_id=flow_id, title=title)

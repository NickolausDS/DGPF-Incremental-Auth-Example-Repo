import json
import logging
import os
from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Field


log = logging.getLogger(__name__)


class TransferForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("endpoint_id", readonly=True),
            Field("path", readonly=True),
        )
        self.helper.add_input(Submit("submit", "Start Transfer"))

    endpoint_id = forms.CharField(
        label="Destination Endpoint",
        max_length=80,
        required=True,
    )

    path = forms.CharField(
        label="Destination Path",
        max_length=80,
        required=True,
    )

DGPF ScopeTest
--------------


This is an example repo to see the different ways you can do incremental auth in DGPF.

What's interesting here?
------------------------

Pretty much everything unique and interesting here is in ``dgpf_scopetest/views.py``.

Setup
-----

If you want to play with the portal, do the following:

Create a dgpf_scopetest.local_settings.py file and add the following: 

.. code-block::

    SOCIAL_AUTH_GLOBUS_KEY = "your key"
    SOCIAL_AUTH_GLOBUS_SECRET = "your secret"


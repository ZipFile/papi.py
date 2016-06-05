import requests

from papi.exceptions import (
    PAPIAuthExpired, PAPIAuthFailed, PAPIException, PAPIMaintenance,
)
from papi.helpers import string_types, urljoin
from papi.pixiv_app import android


class PAPIClient(object):
    URL = "https://public-api.secure.pixiv.net/"
    AUTH_URL = "https://oauth.secure.pixiv.net/auth/token"
    REFERER = "https://public-api.secure.pixiv.net/"
    NO_PROFILE_IMG = "http://source.pixiv.net/common/images/no_profile.png"

    def __init__(self, app=android):
        self.app = app
        self.access_token = app.oauth2.access_token
        self.device_token = None
        self.refresh_token = None

        self.s = requests.Session()
        self.s.headers.update(self.app_headers)
        self.s.headers.update({
            "Referer": self.REFERER,
        })

    def request(self, method, url, error_cls=PAPIException, **kwargs):
        """
        Performs generic request, parses json and raises exceptions on API
        errors (if any).

        `self.resp` holds cached response.
        """
        resp = self.resp = self.s.request(method, url, **kwargs)

        if resp.content == "maintenance":
            raise PAPIMaintenance()

        j = resp.json()

        if "has_error" in j and j["has_error"]:
            msg = j["errors"]["system"]["message"]

            if not isinstance(msg, string_types):
                msg = str(msg)

            _msg = msg.lower()

            if ("access token" in _msg and "invalid" in _msg):
                raise PAPIAuthExpired(msg)

            raise error_cls(msg)

        if not (200 <= resp.status_code < 300):
            raise PAPIException("Unknown exception")

        return j

    def get(self, path, retry=True, **kwargs):
        """
        Perform GET request to the API.

        :param path:   API path.
        :param retry:  If token is invalid, call `self.auth_refresh()` and
                       retry request.
        :param params: Dict of parameters passed as query string.
        :returns:      Response data as dictionary (parsed json).
        """
        try:
            return self.request('GET', urljoin(self.URL, path), **kwargs)
        except PAPIAuthExpired:
            if not retry:
                raise

            self.auth_refresh()

            return self.get(path, False, **kwargs)

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, app):
        device = app.device
        headers = {
            "App-Version": app.version,
        }

        if device and device.os:
            os = device.os
            headers["App-OS"] = os.name.lower()
            headers["App-OS-Version"] = os.version
            headers["User-Agent"] = " ".join([
                "/".join([app.name, app.version]),
                "(%s %s; %s)" % (
                    os.name, os.version, device.model
                )
            ])
        else:
            headers["User-Agent"] = "/".join([app.name, app.version])

        self._app = app
        self._app_headers = headers

    @property
    def app_headers(self):
        return self._app_headers

    def _login_payload(self, username, password):
        oauth2 = self.app.oauth2
        return {
            "client_id": oauth2.client_id,
            "client_secret": oauth2.client_secret,
            # "device_token": "pixiv",
            "grant_type": "password",
            "username": username,
            "password": password,
        }

    def _refresh_token_payload(self):
        oauth2 = self.app.oauth2
        return {
            "client_id": oauth2.client_id,
            "client_secret": oauth2.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def auth_force(self, access_token, refresh_token, device_token=None):
        """
        Provide custom tokens bypassing authentication by password.
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.device_token = device_token

        self.s.headers.update({
            "Authorization": "Bearer " + self.access_token,
        })

    def auth_login(self, username, password):
        """
        Perform OAuth authentication.

        On success `self.user` holds reference to the current user.
        """
        r = self.request(
            'POST',
            self.AUTH_URL,
            error_cls=PAPIAuthFailed,
            data=self._login_payload(username, password)
        )["response"]
        self.user = r["user"]

        self.auth_force(
            r["access_token"], r["refresh_token"], r.get("device_token"),
        )

    def auth_refresh(self):
        """
        Refresh OAuth access token.
        """
        r = self.request(
            'POST',
            self.AUTH_URL,
            error_cls=PAPIAuthFailed,
            data=self._refresh_token_payload()
        )["response"]
        self.user = r["user"]

        self.auth_force(
            r["access_token"], r["refresh_token"], r.get("device_token"),
        )

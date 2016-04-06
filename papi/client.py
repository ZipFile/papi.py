import requests

from papi.exceptions import (
    PAPIAuthExpired, PAPIAuthFailed, PAPIException, PAPIMaintenance,
)
from papi.helpers import string_types
from papi.objects import Emoji
from papi.pixiv_app import android


class PAPIClient(object):
    URL = "https://public-api.secure.pixiv.net/v1"
    AUTH_URL = "https://oauth.secure.pixiv.net/auth/token"
    REFERER = "https://public-api.secure.pixiv.net/"

    def __init__(self, app=android):
        self.app = android
        self.access_token = app.access_token
        self.device_token = None
        self.refresh_token = None

        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": self.app.user_agent,
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
        """Perform GET request to the API.

        :param path:   API path.
        :param retry:  If token is invalid, call `self.auth_refresh()` and
                       retry request.
        :param params: Dict of parameters passed as query string.
        :returns:      Response data as dictionary (parsed json).
        """
        try:
            return self.request('GET', self.URL + path, **kwargs)
        except PAPIAuthExpired:
            if not retry:
                raise

            self.auth_refresh()

            return self.get(path, False, **kwargs)

    def _login_payload(self, username, password):
        return {
            "client_id": self.app.client_id,
            "client_secret": self.app.client_secret,
            # "device_token": "pixiv",
            "grant_type": "password",
            "username": username,
            "password": password,
        }

    def _refresh_token_payload(self):
        return {
            "client_id": self.app.client_id,
            "client_secret": self.app.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def auth_force(self, access_token, refresh_token, device_token=None):
        """Provide custom tokens bypassing authentication by password."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.device_token = device_token

        self.s.headers.update({
            "Authorization": "Bearer " + self.access_token,
        })

    def auth_login(self, username, password):
        """Perform OAuth authentication.

        On success `self.user` holds reference to the current user."""
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
        """Refresh OAuth access token."""
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

    def emojis(self):
        r = self.get("/emojis.json")
        xresp = self.xresp = [Emoji(emoji) for emoji in r["response"]]

        return xresp

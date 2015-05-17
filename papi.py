#/usr/bin/env ipython
import requests


PIXIV_CLIENTS = {
    "android 4.6.0": {
        "user_agent": "PixivAndroidApp/4.6.0",
        "client_id": "BVO2E8vAAikgUBW8FYpi6amXOjQj",
        "client_secret": "LI1WsFUDrrquaINOdarrJclCrkTtc3eojCOswlog",
        "access_token": "8mMXXWT9iuwdJvsVIvQsFYDwuZpRCMePeyagSh30ZdU",
    },
    "ios 5.1.1": {
        "user_agent": "PixivIOSApp/5.1.1",
        "client_id": "bYGKuGVw91e0NMfPGp44euvGt59s",
        "client_secret": "HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK",
        "access_token": None,
    },
}


class PAPIException(Exception):
    pass


class PAPIMaintenance(PAPIException):
    pass


class PAPIAuth(PAPIException):
    pass


class PAPIAuthFailed(PAPIAuth):
    pass


class PAPIAuthExpired(PAPIAuth):
    pass


class PAPIClient:
    url = "https://public-api.secure.pixiv.net/v1"
    auth_url = "https://oauth.secure.pixiv.net/auth/token"
    referrer = "https://public-api.secure.pixiv.net/"

    def __init__(self, client=PIXIV_CLIENTS["android 4.6.0"]):
        self.user_agent = client["user_agent"]
        self.client_id = client["client_id"]
        self.client_secret = client["client_secret"]
        self.access_token = client["access_token"]
        self.refresh_token = None

        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": self.user_agent,
            "Referer": self.referrer,
        })

    def request(self, method, url, error_cls=PAPIException, **kwargs):
        """Performs generic request, parses json and raises exceptions on API
        errors (if any).

        `self.resp` holds cached response."""
        resp = self.resp = self.s.request(method, url, **kwargs)

        if resp.content == "maintenance":
            raise PAPIMaintenance()

        j = resp.json()

        if "has_error" in j and j["has_error"]:
            msg = j["errors"]["system"]["message"]
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
            return self.request('GET', self.url + path, **kwargs)
        except PAPIAuthExpired as e:
            if not retry:
                raise e

            self.auth_refresh()

            return self.get(path, False, **kwargs)

    def _login_payload(self, username, password):
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": username,
            "password": password,
        }

    def _refresh_token_payload(self):
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def auth_force(self, access_token, refresh_token):
        """Provide custom tokens bypassing authentication by password."""
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.s.headers.update({
            "Authorization": "Bearer " + self.access_token,
        })

    def auth_login(self, username, password):
        """Perform OAuth authentication.

        On success `self.user` holds reference to the current user."""
        r = self.request(
            'POST',
            self.auth_url,
            error_cls=PAPIAuthFailed,
            data=self._login_payload(username, password)
        )["response"]
        self.user = r["user"]

        self.auth_force(r["access_token"], r["refresh_token"])

    def auth_refresh(self):
        """Refresh OAuth access token."""
        r = self.request(
            'POST',
            self.auth_url,
            error_cls=PAPIAuthFailed,
            data=self._refresh_token_payload()
        )["response"]
        self.user = r["user"]

        self.auth_force(r["access_token"], r["refresh_token"])


if __name__ == "__main__":
    c = PAPIClient()

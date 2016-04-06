from collections import namedtuple


PixivApp = namedtuple("PixivApp", [
    "user_agent", "client_id", "client_secret", "access_token"
])

android = PixivApp(
    user_agent="PixivAndroidApp/4.6.9",
    client_id="BVO2E8vAAikgUBW8FYpi6amXOjQj",
    client_secret="LI1WsFUDrrquaINOdarrJclCrkTtc3eojCOswlog",
    access_token="8mMXXWT9iuwdJvsVIvQsFYDwuZpRCMePeyagSh30ZdU",
)

ios = PixivApp(
    user_agent="PixivIOSApp/5.8.7",
    client_id="bYGKuGVw91e0NMfPGp44euvGt59s",
    client_secret="HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK",
    access_token=None,
)

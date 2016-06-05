from collections import namedtuple

# NOTE: Model list - https://support.google.com/googleplay/answer/1727131
Device = namedtuple("Device", ["brand", "name", "device", "model", "os"])
OAuth2 = namedtuple("OAuth2", ["client_id", "client_secret", "access_token"])
OS = namedtuple("OS", ["name", "version"])
PixivApp = namedtuple("PixivApp", ["name", "version", "device", "oauth2"])

android = PixivApp(
    "PixivAndroidApp",
    "5.0.17",
    Device("Huawei", "Nexus 6P", "angler", "Nexus 6P", OS("Android", "6.0")),
    OAuth2(
        client_id="BVO2E8vAAikgUBW8FYpi6amXOjQj",
        client_secret="LI1WsFUDrrquaINOdarrJclCrkTtc3eojCOswlog",
        access_token="8mMXXWT9iuwdJvsVIvQsFYDwuZpRCMePeyagSh30ZdU",
    ),
)

ios = PixivApp(
    "PixivIOSApp",
    "5.8.7",
    Device("Apple", "iPhone SE", "iPhone8,4", "A1723", OS("iOS", "9.3.2")),
    OAuth2(
        client_id="bYGKuGVw91e0NMfPGp44euvGt59s",
        client_secret="HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK",
        access_token=None,
    ),
)

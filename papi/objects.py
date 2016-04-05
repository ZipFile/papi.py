from __future__ import division

import re

from papi.helpers import atoi


image_size_rx = re.compile(r"(?:px|max)_(\d+)x(\d+)?")


class PObject(object):
    def parse(self, obj):
        for k, w in obj.items():
            setattr(self, k, w)
        return self

    def __init__(self, obj={}):
        if (obj):
            self.parse(obj)

    def _repr(self):
        return None

    def __repr__(self):
        classname = self.__class__.__name__
        r = self._repr()

        if r:
            return "<%s %s>" % (classname, r)
        else:
            return "<%s>" % (classname, )


class ImageUrls(PObject):
    images = {}
    weights = {
        "large": float("inf"),
        "medium": 360.0,
        "small": 22.5,
        "max_240x240": 57.6,
        "px_120x": 14.4,
        "px_128x128": 16.384,
        "px_16x16": 0.256,
        "px_170x170": 28.9,
        "px_480mw": 337.92,
        "px_48x48": 2.304,
        "px_50x50": 2.5,
        "px_56x56": 3.136,
        "px_64x64": 4.096,
        "ugoira600x600": 360.0,
        "ugoira1920x1080": 2073.6,
    }

    def __delattr__(self, size):
        if size in self.images:
            del self.images[size]

    def __setattr__(self, size, url):
        if size in self.weights:
            weight = self.weights[size]
        else:
            m = image_size_rx.match(size)
            if m:
                width = atoi(m.group(1))
                height = atoi(m.group(2), width)
                weight = width * height / 1000.0
            else:
                weight = 0.0
        self.images[size] = (weight, url)

    def __getattr__(self, key):
        if key in self.images:
            return self.images[key][1]
        else:
            return None

    @property
    def max(self):
        """Get url for largest available image"""
        if not len(self.images):
            return None

        return max(self.images.items(), key=lambda z: z[1][0])[1][1]

    @property
    def all(self):
        return [(k, w[1]) for k, w in self.images.items()]

    def parse(self, obj):
        self.images.clear()

        return super(ImageUrls, self).parse(obj)

    def __init__(self, obj={}):
        self.parse(obj)

    def _repr(self):
        return ", ".join(self.images.keys())


class Emoji(PObject):
    def parse(self, obj):
        _obj = obj.copy()
        _obj["image_urls"] = ImageUrls(obj.get("image_urls", {}))

        return super(Emoji, self).parse(_obj)

    def _repr(self):
        return self.slug

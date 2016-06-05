# papi.py
See https://gist.github.com/ZipFile/e14ff1a7e6d01456188a for API documentation.

## Install

```sh
cd papi.py
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

## Usage

```python
from papi import PAPIClient

client = PAPIClient()

client.auth_login("username", "password")

# Get full-sized images of top10 original works on May 3 2015
params = {
  "mode": "original",
  "page": 1,
  "per_page": 10,
  "date":"2015-05-03",
  "image_sizes": "large"
}
resp = client.get("/v1/ranking/all", params=params)
urls = list(map(lambda x: x["work"]["image_urls"]["large"], resp["response"][0]["works"]))
print("\n".join(urls))
```

from datetime import datetime
from pytz import timezone
import urllib, hashlib


# Set your variables here
def gravatar_url(email: str) -> str:
    if not email:
        return ""
    size = 50
    encoded_email = email.encode("utf-8").lower()
    gravatar_url = (
        "https://www.gravatar.com/avatar/"
        + hashlib.md5(encoded_email).hexdigest()
        + "?"
    )
    gravatar_url += urllib.parse.urlencode({"s": str(size)})
    return gravatar_url


def camelcase(s: str) -> str:
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)

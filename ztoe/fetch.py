import http.client
import urllib.request

URL = "https://www.ztoe.com.ua/unhooking-search.php"
ENCODING = "cp1251"
TIMEOUT_SECONDS = 30
USER_AGENT = "Mozilla/5.0"
NETWORK_ERRORS = (OSError, http.client.HTTPException)


def fetch_html():
    request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read().decode(ENCODING, errors="replace")

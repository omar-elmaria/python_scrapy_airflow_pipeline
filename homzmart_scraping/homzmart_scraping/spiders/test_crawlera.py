# Must set the user type to "Smart Proxy Manager"
import requests

url = "http://httpbin.org/ip"
proxy_host = "proxy.zyte.com"
proxy_port = "8011"
proxy_auth = "3c9fb0a16f1e4af084e65c6b2037ea3e:" # Make sure to include ':' at the end
proxies = {"https": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
      "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}

r = requests.get(
    url,
    proxies=proxies,
    verify='/usr/local/share/ca-certificates/zyte-smartproxy-ca.crt',
)

print(
    f"Requesting [{url}]\n\n"
    f"through proxy [{proxy_host}]\n\n"
    "Request Headers:"
    f"{r.request.headers}\n\n"
    f"Response Time: {r.elapsed.total_seconds()}\n\n"
    f"Response Code: {r.status_code}\n\n"
    f"Response Headers: {r.headers}\n\n"
    f"Response Cookies: {r.cookies.items()}\n\n"
    f"Response Body: {r.text}\n"
)
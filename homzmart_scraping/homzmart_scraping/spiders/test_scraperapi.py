from cgi import print_directory
import requests

payload = {'api_key': 'a66ccf7b65589c9068093127373713af', 'url': 'https://httpbin.org/ip'}
r = requests.get('http://api.scraperapi.com', params=payload)

print(r.text)
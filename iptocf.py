import requests
from requests_toolbelt.adapters import source
import json
import sys
import time
import urllib3

# Internal IP of the interface you want to use.
INTERNAL_IP = '192.168.10.101'
# Cloudflare API Key: (https://support.cloudflare.com/hc/en-us/articles/200167836-Where-do-I-find-my-Cloudflare-API-key- ).
CF_API_KEY = 'XXXxxxXXxxxXXxxxx'
# Your Cloudflare email address.
CF_EMAIL = 'xxxxx@xxxxx.com'
# Your zone id is located on the main Cloudflare domain dashboard.
ZONE_ID = 'XXXxxxXXxxxXXxxxx'
# Run script once without this set and it'll retrive a list of records for you to find the ID to update here.
RECORD_ID = ''
# CF DNS zone name.
CF_NAME = 'xxxxxx.com'
# Amount of time for script to sleep in seconds.
TIMER = 60

headers = {
    'X-Auth-Key': CF_API_KEY,
    'X-Auth-Email': CF_EMAIL
}

rSession = requests.Session()
inetface = source.SourceAddressAdapter(INTERNAL_IP)
rSession.mount('http://', inetface)
rSession.mount('https://', inetface)
externalIPURL = 'https://api.ipify.org/?format=json'
response = rSession.get(externalIPURL)
ip = response.json()['ip']

cfjson = {
    'type': 'A',
    'name': CF_NAME,
    'content': ip,
    'proxied': False
}

if not RECORD_ID:
    try:
        response = requests.get(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(ZONE_ID),
            headers=headers)
        rjson = response.json()['result']
        zone_name = str()
        for data in rjson:
            zone_name = data.get('zone_name', '')
            name = data.get('name', '')
            zone_id = data.get('zone_id', 0)
            print(name, zone_id)
        assert response.status_code == 200
    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[IPTOCF] urllib3 ERROR:", de)
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[IPTOCF] requests ERROR:", ce)
    except TypeError as t:
        print("[IPTOCF] TypeError ERROR:", t)
    except AssertionError as a:
        print("[IPTOCF] AssertionError ERROR:", a)
    print('[IPTOCF] Please Find The DNS Record ID And Update The Script For', zone_name)
    sys.exit(0)

while True:
    try:
        response = requests.put(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(ZONE_ID, RECORD_ID),
            json=cfjson, headers=headers)
        rjson = response.json()['result']
        id = rjson.get('id', 0)
        zone_id = rjson.get('zone_id', 0)
        zone_name = rjson.get('zone_name', '')
        name = rjson.get('name', '')
        type = rjson.get('type', '')
        content = rjson.get('content', '')
        created_on = rjson.get('created_on', 0)
        modified_on = rjson.get('modified_on', 0)

        assert response.status_code == 200
    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[IPTOCF] urllib3 ERROR:", de)
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[IPTOCF] requests ERROR:", ce)
    except TypeError as t:
        print("[IPTOCF] TypeError ERROR:", t)
    except AssertionError as a:
        print("[IPTOCF] AssertionError ERROR:", a)
    print('[IPTOCF] Updated DNS Record For', name, str(ip), created_on, modified_on)
    time.sleep(TIMER)

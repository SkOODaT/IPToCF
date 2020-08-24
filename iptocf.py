import requests
from requests_toolbelt.adapters import source
import json
import sys
import time
import urllib3

with open('configs.json', 'r') as f:
    configs = json.load(f)
    print("[IPTOCF] Configuration Loaded")

headers = {
    'X-Auth-Key': configs['CF_API_KEY'],
    'X-Auth-Email': configs['CF_EMAIL']
}

externalIPURL = 'https://api.ipify.org/?format=json'

if configs['INTERNAL_IP'] and configs['CF_TYPE'] and configs['CF_NAME']:
    rSession = requests.Session()
    inetface = source.SourceAddressAdapter(configs['INTERNAL_IP'])
    rSession.mount('http://', inetface)
    rSession.mount('https://', inetface)
    response = rSession.get(externalIPURL)
    ip = response.json()['ip']

    cfjson = {
        'type': configs['CF_TYPE'],
        'name': configs['CF_NAME'],
        'content': ip,
        'proxied': False
    }

if configs['INTERNAL_IP_2'] and configs['CF_TYPE_2'] and configs['CF_NAME_2']:
    rSession2 = requests.Session()
    inetface2 = source.SourceAddressAdapter(configs['INTERNAL_IP_2'])
    rSession2.mount('http://', inetface2)
    rSession2.mount('https://', inetface2)
    response2 = rSession2.get(externalIPURL)
    ip2 = response2.json()['ip']
    cfjson2 = {
        'type': configs['CF_TYPE_2'],
        'name': configs['CF_NAME_2'],
        'content': ip2,
        'proxied': False
    }

if not configs['RECORD_ID'] and configs['ZONE_ID']:
    try:
        response = requests.get(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(configs['ZONE_ID']),
            headers=headers)
        rjson = response.json()['result']
        zone_name = str()
        for data in rjson:
            zone_name = data.get('zone_name', '')
            name = data.get('name', '')
            id = data.get('id', 0)
            print('[{}] {}'.format(name, id))
        assert response.status_code == 200
    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[IPTOCF] urllib3 ERROR: {}".format(de))
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[IPTOCF] requests ERROR: {}".format(ce))
    except TypeError as t:
        print("[IPTOCF] TypeError ERROR: {}".format(t))
    except AssertionError as a:
        print("[IPTOCF] AssertionError ERROR: {}".format(a))
    if configs['DEBUG'] == 'True':
        print(json.dumps(response.json(), indent=4, sort_keys=True))
    print('[IPTOCF] Please Find The DNS Record ID And Update The Script For {}'.format(zone_name))
    sys.exit(0)

if not configs['RECORD_ID_2'] and configs['ZONE_ID_2']:
    try:
        response2 = requests.get(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(configs['ZONE_ID_2']),
            headers=headers)
        rjson = response2.json()['result']
        zone_name = str()
        for data in rjson:
            zone_name = data.get('zone_name', '')
            name = data.get('name', '')
            id = data.get('id', 0)
            print('[{}] {}'.format(name, id))
        assert response2.status_code == 200
    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[IPTOCF] urllib3 ERROR: {}".format(de))
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[IPTOCF] requests ERROR: {}".format(ce))
    except TypeError as t:
        print("[IPTOCF] TypeError ERROR: {}".format(t))
    except AssertionError as a:
        print("[IPTOCF] AssertionError ERROR: {}".format(a))
    if configs['DEBUG'] == 'True':
        print(json.dumps(response2.json(), indent=4, sort_keys=True))
    print('[IPTOCF] Please Find The DNS Record ID And Update The Script For {}'.format(zone_name))
    if not configs['RECORD_ID']:
        sys.exit(0)

while True:
    if configs['ZONE_ID'] and configs['RECORD_ID']:
        try:
            response = requests.put(
                'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(configs['ZONE_ID'], configs['RECORD_ID']),
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
            print("[IPTOCF] urllib3 ERROR: {}".format(de))
        except requests.exceptions.ConnectionError as ce:
            retry_error = True
            print("[IPTOCF] requests ERROR: {}".format(ce))
        except TypeError as t:
            print("[IPTOCF] TypeError ERROR: {}".format(t))
        except AssertionError as a:
            print("[IPTOCF] AssertionError ERROR: {}".format(a))
        if configs['DEBUG'] == 'True':
            print(json.dumps(response.json(), indent=4, sort_keys=True))
        print('[IPTOCF] Updated DNS Record For {} {} [{}] {}'.format(name, content, zone_id, modified_on))
    if configs['ZONE_ID_2'] and configs['RECORD_ID_2']:
        try:
            response2 = requests.put(
                'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(configs['ZONE_ID_2'], configs['RECORD_ID_2']),
                json=cfjson2, headers=headers)
            rjson = response2.json()['result']
            id = rjson.get('id', 0)
            zone_id = rjson.get('zone_id', 0)
            zone_name = rjson.get('zone_name', '')
            name = rjson.get('name', '')
            type = rjson.get('type', '')
            content = rjson.get('content', '')
            created_on = rjson.get('created_on', 0)
            modified_on = rjson.get('modified_on', 0)
            assert response2.status_code == 200
        except urllib3.exceptions.ProtocolError as de:
            retry_error = True
            print("[IPTOCF] urllib3 ERROR: {}".format(de))
        except requests.exceptions.ConnectionError as ce:
            retry_error = True
            print("[IPTOCF] requests ERROR: {}".format(ce))
        except TypeError as t:
            print("[IPTOCF] TypeError ERROR: {}".format(t))
        except AssertionError as a:
            print("[IPTOCF] AssertionError ERROR: {}".format(a))
        if configs['DEBUG'] == 'True':
            print(json.dumps(response2.json(), indent=4, sort_keys=True))
        print('[IPTOCF] Updated DNS Record For {} {} [{}] {}'.format(name, content, zone_id, modified_on))
    try:
        time.sleep(configs['TIMER'])
    except KeyboardInterrupt:
        print("[IPTOCF] Exited...")
        sys.exit(0)
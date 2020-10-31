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

# Get Initial Config Datas [Zone ID] And [Name]
def GetConfigData():
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
            response.close()
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

# Main Cloud Flare IP Update
def UpdateCloudFlareIP():
    while True:
        if configs['ZONE_ID'] and configs['RECORD_ID']:
            try:
                cfjson = GetExternalIP() # Update External IP For CF
                response = requests.put(
                    'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(configs['ZONE_ID'], configs['RECORD_ID']),
                    json=cfjson, headers=headers)
                rjson = response.json()['result']
                response.close()
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
            #print(rjson)
            id = rjson.get('id', 0)
            zone_id = rjson.get('zone_id', 0)
            zone_name = rjson.get('zone_name', '')
            name = rjson.get('name', '')
            type = rjson.get('type', '')
            content = rjson.get('content', '')
            created_on = rjson.get('created_on', 0)
            modified_on = rjson.get('modified_on', 0)
            assert response.status_code == 200
            if configs['DEBUG'] == 'True':
                print(json.dumps(response.json(), indent=4, sort_keys=True))
            print('[IPTOCF] Updated DNS Record For {} {} [{}] {}'.format(name, content, zone_id, modified_on))
        try:
            time.sleep(configs['TIMER'])
        except KeyboardInterrupt:
            print("[IPTOCF] Exited...")
            sys.exit(0)

# Get External IP For UpdateCloudFlareIP() Based Off Specific Internal Adaptor 
def GetExternalIP():
    externalIPURL = 'https://api.ipify.org/?format=json'
    if configs['INTERNAL_IP'] and configs['CF_TYPE'] and configs['CF_NAME']:
        ip = int()
        try:
            response = requests.Session()
            inetface = source.SourceAddressAdapter(configs['INTERNAL_IP'])
            response.mount('http://', inetface)
            response.mount('https://', inetface)
            rSession = response.get(externalIPURL)
            response.close()
            ip = rSession.json()['ip']
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
        cfjson = {
            'type': configs['CF_TYPE'],
            'name': configs['CF_NAME'],
            'content': ip,
            'proxied': True
        }
    return cfjson

# Run The Functions In Order
GetConfigData()
UpdateCloudFlareIP()
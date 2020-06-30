#!/usr/bin/env python
import argparse
import re
import requests
import yaml


def get_auth_token(directory_id, client_id, client_secret):
    url = f'https://login.microsoftonline.com/{directory_id}/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.azure.com'
    }
    response = requests.request('GET', url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def get_nsgs(subscription_id, auth_token):
    url = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Network/networkSecurityGroups?api-version=2020-05-01'
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    response = requests.get(url, headers=headers )

    nsgs = []
    for i in response.json()["value"]:
        nsgs.append({
            "name": i['name'],
            'id': i['id'],
            'location': i['location'],
            'resource_group': re.findall(r'resourceGroups\/(.+)\/providers', i['id'])[0]
        })
    return nsgs


def enable_nsg_flows(subscription_id, location, nsg_rg, nsg_name, storage_id, auth_token):
    url = f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_{location}/configureFlowLog?api-version=2020-05-01'

    payload = {
        "targetResourceId": f"/subscriptions/{subscription_id}/resourceGroups/{nsg_rg}/providers/Microsoft.Network/networkSecurityGroups/{nsg_name}",
        "properties": {
            "storageId": storage_id,
            "enabled": True,
            "retentionPolicy": {
                "days": 7,
                "enabled": True
            },
            "format": {
                "type": "JSON",
                "version": 2
            }
        }
    }
    headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json'
    }
  
    response = requests.request("POST", url, headers=headers, json = payload)
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('subscription_name', help='Name of the subscription to target, match name in config.ini')
    args = parser.parse_args()
    with open('config.yml') as f:
        config = yaml.safe_load(f)
    subscription_id = config['subscriptions'][args.subscription_name]
    storage_id = config['storage_id']
    bear_token = get_auth_token(
        config['service_principal']['directory_id'],
        config['service_principal']['client_id'],
        config['service_principal']['client_secret'])['access_token']
    for nsg in get_nsgs(subscription_id, bear_token):
        status = enable_nsg_flows(subscription_id, nsg['location'], nsg['resource_group'], nsg['name'], storage_id, bear_token)
        if status.ok:
            print(f'{nsg["name"]}: {status.status_code} {status.reason}')
        else:
            print(f'{nsg["name"]}: {status.status_code} {status.reason} {status.json()["error"]["message"]}\n')

if __name__ == '__main__':
    main()

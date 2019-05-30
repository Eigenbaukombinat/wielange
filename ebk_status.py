import requests

def is_open():
    """returns true if the eigenbaukombinat is open, false if not.
    if there was an error getting the status, it returns None"""
    resp = requests.get('https://eigenbaukombinat.de/status/status.json')
    if resp.ok:
        data = resp.json()
        return data['state']['open']

import time
import os
import requests
import urllib
import base64
import hmac
import hashlib
import pprint
import time
import datetime
import signal

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("exiting...")
        self.kill_now = True


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


killer = GracefulKiller()
api_url = "https://api.kraken.com"
api_key = os.environ['API_KEY_KRAKEN']
api_sec = os.environ['API_SEC_KRAKEN']
interval = os.environ.get('LOOP_INTERVAL', 600)


while not killer.kill_now:
    try:
        now = time.time()
        if os.environ.get("STAKED_ASSET"):
            staked_asset = os.environ["STAKED_ASSET"]
            resp = kraken_request('/0/private/Staking/Transactions', {
                "nonce": str(int(1000*time.time())),
                "asset": staked_asset,
                "start": int(time.time() - 3600*24*7)
            }, api_key, api_sec)
            print("checking for rewards from staked {}".format(staked_asset))
            last_reward_transaction = None
            for transaction in sorted(resp.json()["result"], key=lambda tra: tra["time"]):
                if transaction["type"] == "reward" and transaction["asset"] == staked_asset and transaction["time"] >= now - interval:
                    last_reward_transaction = transaction
            if last_reward_transaction:
                # Reward (Gegenwert in EUR) wird versteuert: sonstige Einkünfte, §22.4
                # Tokens gelten als angeschafft zum Marktkurs im Moment des Rewards
                # Unmittelbarer Verkauf:
                #  Da kein Kursgewinn, ist der Verkauferlös steuerfrei
                print("reward: {} {}".format(datetime.datetime.fromtimestamp(last_reward_transaction["time"]), last_reward_transaction["amount"], last_reward_transaction["asset"]))
                if os.environ.get("ASSET_PAIR"):
                    resp = kraken_request('/0/private/AddOrder', {
                        "nonce": str(int(1000*time.time())),
                        "ordertype": "market",
                        "type": "sell",
                        "volume": last_reward_transaction["amount"],
                        "pair": os.environ["ASSET_PAIR]"
                    }, api_key, api_sec)

        for _ in range(interval):
            if not killer.kill_now:
                time.sleep(1)
    except KeyboardInterrupt:
        self.exit_gracefully(None, None)

print("good bye")

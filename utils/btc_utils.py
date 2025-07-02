import requests
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip86, Bip44Coins, Bip49Coins, Bip84Coins, Bip86Coins, \
    Bip44Changes

from wallet_profiles import WALLET_PROFILES

ADDRESS_TYPE_CLASSES = {
    "legacy": (Bip44, Bip44Coins.BITCOIN),
    "p2sh": (Bip49, Bip49Coins.BITCOIN),
    "bech32": (Bip84, Bip84Coins.BITCOIN),
    "taproot": (Bip86, Bip86Coins.BITCOIN),
}

def process_seed(seed_phrase, address_types, profile_name, address_depth=20, account_depth=5):
    print("[BTC] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    path_templates = WALLET_PROFILES.get(profile_name)

    if not path_templates:
        print(f"[BTC] No derivation paths found for profile: {profile_name}")
        return wallets

    for addr_type in address_types:
        if addr_type not in ADDRESS_TYPE_CLASSES:
            print(f"[BTC] Unsupported address type: {addr_type}")
            continue

        bip_class, bip_coin = ADDRESS_TYPE_CLASSES[addr_type]
        print(f"[BTC] Scanning address type '{addr_type}' for seed: {seed_phrase[:8]}...")

        for path_template in path_templates:
            for account in range(account_depth):
                for index in range(address_depth):
                    try:
                        path = path_template.replace("{account}", str(account)).replace("{index}", str(index))
                        bip_obj = bip_class.FromSeed(seed_bytes, bip_coin)
                        addr_obj = bip_obj.DerivePath(path)

                        address = addr_obj.PublicKey().ToAddress()
                        private_key = addr_obj.PrivateKey().Raw().ToHex()

                        balance = get_btc_balance(address)
                        if balance and balance > 0:
                            print(f"[BTC] {path} ({addr_type}) – Balance: {balance}")
                            wallets.append({
                                "network": "BTC",
                                "type": addr_type,
                                "profile": profile_name,
                                "path": path,
                                "address": address,
                                "private_key": private_key,
                                "balance": str(balance)
                            })

                    except Exception as e:
                        print(f"[BTC] Error deriving {path} ({addr_type}): {e}")

    print("[BTC] Done.")
    return wallets

def get_btc_balance(address):
    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
        r = requests.get(url)
        if 'error' in r.json():
            print(f"[BTC] Error fetching balance for {address}: {r.json()['error']}")
            return None
        data = r.json()
        return data.get("final_balance", 0) / 1e8
    except Exception as e:
        print(f"[BTC] Error fetching balance for {address}: {e}")
        return None

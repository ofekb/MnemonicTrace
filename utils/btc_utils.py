import requests
from bip_utils import (
    Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip86,
    Bip44Coins, Bip49Coins, Bip84Coins, Bip86Coins,
    Bip44Changes
)

# Map address types to BIP class and the correct Coin enum
SUPPORTED_BTC_ADDRESS_TYPES = {
    "legacy":   (Bip44, Bip44Coins.BITCOIN),
    "p2sh":     (Bip49, Bip49Coins.BITCOIN),
    "bech32":   (Bip84, Bip84Coins.BITCOIN),
    "taproot":  (Bip86, Bip86Coins.BITCOIN),
}



def process_seed(seed_phrase, address_types):
    print("[BTC] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()

    for addr_type in address_types:
        try:
            bip_class, coin_enum = SUPPORTED_BTC_ADDRESS_TYPES[addr_type]
        except KeyError:
            print(f"[BTC] Unsupported address type: {addr_type}")
            continue

        print(f"[BTC] Scanning address type '{addr_type}' for seed: {seed_phrase[:8]}...")

        try:
            bip_obj = bip_class.FromSeed(seed_bytes, coin_enum)
        except Exception as e:
            print(f"[BTC] Error initializing {addr_type}: {e}")
            continue

        for i in range(20):
            print(f"[BTC] Deriving address #{i}...")
            try:
                addr = bip_obj.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
                address = addr.PublicKey().ToAddress()
                private_key = addr.PrivateKey().Raw().ToHex()

                balance = get_btc_balance(address)
                if balance is not None and balance > 0:
                    print(f"[BTC] Address #{i} ({addr_type}) – Balance: {balance}")
                    wallets.append({
                        "network": "BTC",
                        "type": addr_type,
                        "index": i,
                        "address": address,
                        "private_key": private_key,
                        "balance": str(balance)
                    })
            except Exception as e:
                print(f"[BTC] Error index #{i} type {addr_type}: {e}")

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

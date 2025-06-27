from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import requests

def process_seed(seed_phrase):
    print("[BTC] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip_obj = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)

    for i in range(20):
        print(f"[BTC] Deriving address #{i}...")
        addr = bip_obj.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
        address = addr.PublicKey().ToAddress()
        private_key = addr.PrivateKey().Raw().ToHex()

        balance = get_btc_balance(address)
        if float(balance) > 0:
            print(f"[BTC] BTC balance for {address}: {balance}")
            wallets.append({
                "network": "Bitcoin",
                "address": address,
                "private_key": private_key,
                "assets": [{
                    "symbol": "BTC",
                    "amount": balance
                }]
            })

    print("[BTC] Done.")
    return wallets

def get_btc_balance(address):
    try:
        url = f"https://blockstream.info/api/address/{address}"
        r = requests.get(url)
        data = r.json()
        confirmed = data.get("chain_stats", {}).get("funded_txo_sum", 0)
        spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
        balance = (confirmed - spent) / 1e8
        return str(balance)
    except Exception as e:
        print(f"[BTC] Error getting BTC balance: {e}")
        return "0"
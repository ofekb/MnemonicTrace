from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import requests
import os

from config import BSCSCAN_API_KEY


def process_seed(seed_phrase):
    print("[BNB] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip = Bip44.FromSeed(seed_bytes, Bip44Coins.BINANCE_SMART_CHAIN)

    for i in range(20):
        print(f"[BSC] Deriving address #{i}...")
        try:
            addr = bip.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
            address = addr.PublicKey().ToAddress()
            private_key = addr.PrivateKey().Raw().ToHex()

            info = get_bnb_wallet_info(address)
            total = float(info["bnb"]) + sum([float(t["amount"]) for t in info["tokens"]])

            if total > 0:
                print(f"[BNB] Address #{i} – Total Balance: {total}")
                wallets.append({
                    "network": "BNB",
                    "address": address,
                    "private_key": private_key,
                    "bnb": info["bnb"],
                    "tokens": info["tokens"]
                })
        except Exception as e:
            print(f"[BNB] Error address #{i}: {e}")

    print("[BNB] Done.")
    return wallets


def get_bnb_wallet_info(address):
    result = {"bnb": "0", "tokens": []}
    try:
        # BNB balance
        url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={BSCSCAN_API_KEY}"
        r = requests.get(url)
        data = r.json()
        bnb_raw = data.get("result", "0")

        if isinstance(bnb_raw, str) and 'rate limit' in bnb_raw.lower():
            print(f"[BNB] Rate limit reached (BNB): {bnb_raw}")
            return result

        try:
            bnb_balance = str(int(bnb_raw) / 1e18)
            result["bnb"] = bnb_balance
        except Exception as e:
            print(f"[BNB] Error parsing BNB balance: {e} | Value: {bnb_raw}")
            return result

        # Token balances
        url_tokens = f"https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={{}}&address={address}&tag=latest&apikey={BSCSCAN_API_KEY}"
        tokens = {
            "USDT": "0x55d398326f99059fF775485246999027B3197955",
            "USDC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"
        }

        for symbol, contract in tokens.items():
            try:
                r = requests.get(url_tokens.format(contract))
                token_data = r.json()
                token_raw = token_data.get("result", "0")

                if isinstance(token_raw, str) and 'rate limit' in token_raw.lower():
                    print(f"[BNB] Rate limit reached ({symbol}): {token_raw}")
                    continue

                try:
                    value = int(token_raw) / 1e18
                    if value > 0:
                        print(f"[BNB] Token {symbol} – {value}")
                        result["tokens"].append({
                            "symbol": symbol,
                            "contract": contract,
                            "amount": str(value)
                        })
                except Exception as e:
                    print(f"[BNB] Error parsing {symbol} balance: {e} | Value: {token_raw}")
            except Exception as e:
                print(f"[BNB] Error fetching {symbol}: {e}")

    except Exception as e:
        print(f"[BNB] Error for {address}: {e}")

    return result
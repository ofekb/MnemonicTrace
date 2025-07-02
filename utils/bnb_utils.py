from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip32Slip10Secp256k1, EthAddr
import requests
import os

from config import BSCSCAN_API_KEY
from wallet_profiles import WALLET_PROFILES


def process_seed(seed_phrase, profile_name, address_depth=20, account_depth=5):
    print("[BNB] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    derivation_templates = WALLET_PROFILES.get(profile_name)

    if not derivation_templates:
        print(f"[BNB] No derivation paths found for profile: {profile_name}")
        return wallets

    if isinstance(derivation_templates, list):
        # Static paths
        for path_template in derivation_templates:
            for i in range(address_depth):
                path = path_template.replace("i", str(i))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    address = EthAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    print(f"[BSC] Deriving {path}...")

                    info = get_bnb_wallet_info(address)
                    total = float(info["bnb"]) + sum([float(t["amount"]) for t in info["tokens"]])

                    if total > 0:
                        print(f"[BNB] Address {path} – Total Balance: {total}")
                        wallets.append({
                            "network": "BNB",
                            "address": address,
                            "private_key": private_key,
                            "bnb": info["bnb"],
                            "tokens": info["tokens"]
                        })
                except Exception as e:
                    print(f"[BNB] Error deriving {path}: {e}")
    else:
        # Dynamic paths (e.g., Ledger Live)
        template = derivation_templates  # e.g., "m/44'/60'/{account}'/0/{index}"
        for account in range(account_depth):
            for index in range(address_depth):
                path = template.replace("{account}", str(account)).replace("{index}", str(index))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    address = EthAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    print(f"[BSC] Deriving {path}...")

                    info = get_bnb_wallet_info(address)
                    total = float(info["bnb"]) + sum([float(t["amount"]) for t in info["tokens"]])

                    if total > 0:
                        print(f"[BNB] Address {path} – Total Balance: {total}")
                        wallets.append({
                            "network": "BNB",
                            "address": address,
                            "private_key": private_key,
                            "bnb": info["bnb"],
                            "tokens": info["tokens"]
                        })
                except Exception as e:
                    print(f"[BNB] Error deriving {path}: {e}")

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
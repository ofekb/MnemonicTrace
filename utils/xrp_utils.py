from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip32Slip10Secp256k1, XrpAddr
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo, AccountLines

from config import XRPL_API_ENDPOINT
from wallet_profiles import WALLET_PROFILES

client = JsonRpcClient(XRPL_API_ENDPOINT)  # XRP mainnet public node


def process_seed(seed_phrase, profile_name, address_depth=20, account_depth=5):
    print("[XRP] Starting...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    derivation_templates = WALLET_PROFILES.get(profile_name)

    if not derivation_templates:
        print(f"[XRP] No derivation paths found for profile: {profile_name}")
        return wallets

    if isinstance(derivation_templates, list):
        # Static profiles
        for path_template in derivation_templates:
            for i in range(address_depth):
                path = path_template.replace("i", str(i))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    address = XrpAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    info = get_xrp_balance(address)
                    xrp_amount = float(info["XRP"])
                    token_amount = sum([float(t["amount"]) for t in info["tokens"]])
                    total = xrp_amount + token_amount

                    if total > 0:
                        print(f"[XRP] Address {path} – Balance: {total}")
                        wallets.append({
                            "network": "XRP",
                            "address": address,
                            "private_key": private_key,
                            "assets": [{"symbol": "XRP", "amount": xrp_amount}] + info["tokens"]
                        })
                except Exception as e:
                    print(f"[XRP] Error deriving {path}: {e}")
    else:
        # Dynamic profiles (e.g., Ledger Live)
        template = derivation_templates  # e.g., "m/44'/144'/{account}'/0/{index}"
        for account in range(account_depth):
            for index in range(address_depth):
                path = template.replace("{account}", str(account)).replace("{index}", str(index))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    address = XrpAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    info = get_xrp_balance(address)
                    xrp_amount = float(info["XRP"])
                    token_amount = sum([float(t["amount"]) for t in info["tokens"]])
                    total = xrp_amount + token_amount

                    if total > 0:
                        print(f"[XRP] Address {path} – Balance: {total}")
                        wallets.append({
                            "network": "XRP",
                            "address": address,
                            "private_key": private_key,
                            "assets": [{"symbol": "XRP", "amount": xrp_amount}] + info["tokens"]
                        })
                except Exception as e:
                    print(f"[XRP] Error deriving {path}: {e}")

    return wallets

def get_xrp_balance(address):
    result = {"XRP": 0.0, "tokens": []}
    try:
        acct_info = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True
        )
        response = client.request(acct_info)
        res = response.result

        if isinstance(res, dict) and "account_data" in res:
            balance_drops = int(res["account_data"]["Balance"])
            result["XRP"] = balance_drops / 1_000_000
        else:
            print(f"[XRP] No 'account_data' found for {address}")
    except Exception as e:
        print(f"[XRP] Error getting XRP balance for {address}: {e}")

    try:
        acct_lines = AccountLines(
            account=address,
            ledger_index="validated"
        )
        response = client.request(acct_lines)
        res = response.result

        if isinstance(res, dict) and "lines" in res:
            for line in res["lines"]:
                symbol = line.get("currency", "UNKNOWN")
                balance = float(line.get("balance", "0"))
                if balance != 0:
                    result["tokens"].append({
                        "symbol": symbol,
                        "issuer": line.get("account", ""),
                        "amount": balance
                    })
        else:
            print(f"[XRP] No 'lines' found for {address}")
    except Exception as e:
        print(f"[XRP] Error getting token balances for {address}: {e}")

    return result


# Example usage:
# print(get_xrp_wallets("your 24-word seed phrase here"))

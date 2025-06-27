from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo, AccountLines

from config import XRPL_API_ENDPOINT

client = JsonRpcClient(XRPL_API_ENDPOINT)  # XRP mainnet public node


def process_seed(seed_phrase):
    print("[XRP] Starting...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip = Bip44.FromSeed(seed_bytes, Bip44Coins.RIPPLE)

    for i in range(20):
        try:
            addr = bip.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
            address = addr.PublicKey().ToAddress()
            private_key = addr.PrivateKey().Raw().ToHex()

            info = get_xrp_balance(address)
            xrp_amount = float(info["XRP"])
            token_amount = sum([float(t["amount"]) for t in info["tokens"]])
            total = xrp_amount + token_amount

            if total > 0:
                print(f"[XRP] Address #{i} – Balance: {total}")
                wallets.append({
                    "network": "XRP",
                    "address": address,
                    "private_key": private_key,
                    "assets": [{"symbol": "XRP", "amount": xrp_amount}] + info["tokens"]
                })
        except Exception as e:
            print(f"[XRP] Error address #{i}: {e}")
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

import json
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip32Slip10Secp256k1, SolAddr

from config import SOLANA_RPC_URL
from wallet_profiles import WALLET_PROFILES

client = Client(SOLANA_RPC_URL)

TOKEN_SYMBOLS = {
    "Es9vMFrzaCERtPj1T6Q2kCezW4NB6C8Dw1JNKYfYzExv": "USDT",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8nndxrnbWgFLoXg": "USDC",
}

def process_seed(seed_phrase: str, profile_name: str, address_depth: int = 20, account_depth: int = 5):
    print("[SOLANA] Starting wallet derivation...")
    wallets = []

    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    derivation_templates = WALLET_PROFILES.get(profile_name)

    if not derivation_templates:
        print(f"[SOLANA] No derivation paths found for profile: {profile_name}")
        return wallets

    if isinstance(derivation_templates, list):
        # Static profiles
        for path_template in derivation_templates:
            for i in range(address_depth):
                path = path_template.replace("i", str(i))
                try:
                    addr_ctx = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    priv_key = addr_ctx.PrivateKey().Raw().ToHex()
                    pub_addr = SolAddr.EncodeKey(addr_ctx.PublicKey().KeyObject())

                    print(f"[SOLANA] Deriving {path}...")

                    info = get_solana_wallet_info(pub_addr)
                    total = info["SOL"] + sum([t["amount"] for t in info["tokens"]])

                    if total > 0:
                        print(f"[SOLANA] Found balance at {pub_addr}!")
                        wallets.append({
                            "network": "SOLANA",
                            "address": pub_addr,
                            "private_key": priv_key,
                            "sol": info["SOL"],
                            "tokens": info["tokens"]
                        })
                except Exception as e:
                    print(f"[SOLANA] Error at {path}: {e}")
    else:
        # Dynamic profile like Ledger
        template = derivation_templates  # e.g., "m/44'/501'/{account}'/0/{index}"
        for account in range(account_depth):
            for index in range(address_depth):
                path = template.replace("{account}", str(account)).replace("{index}", str(index))
                try:
                    addr_ctx = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    priv_key = addr_ctx.PrivateKey().Raw().ToHex()
                    pub_addr = SolAddr.EncodeKey(addr_ctx.PublicKey().KeyObject())

                    print(f"[SOLANA] Deriving {path}...")

                    info = get_solana_wallet_info(pub_addr)
                    total = info["SOL"] + sum([t["amount"] for t in info["tokens"]])

                    if total > 0:
                        print(f"[SOLANA] Found balance at {pub_addr}!")
                        wallets.append({
                            "network": "SOLANA",
                            "address": pub_addr,
                            "private_key": priv_key,
                            "sol": info["SOL"],
                            "tokens": info["tokens"]
                        })
                except Exception as e:
                    print(f"[SOLANA] Error at {path}: {e}")

    print("[SOLANA] Done.")
    return wallets


def get_solana_wallet_info(address: str):
    result = {"SOL": 0.0, "tokens": []}
    try:
        # Get SOL balance
        sol = client.get_balance(Pubkey.from_string(address)).value / 1e9
        #print(f"[SOLANA] SOL balance for {address}: {sol}")
        result["SOL"] = sol

        # Raw JSON-RPC call
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }

        http_resp = client._provider.session.post(client._provider.endpoint_uri, json=payload)
        data = http_resp.json()

        accounts = data.get("result", {}).get("value", [])
        for acc in accounts:
            try:
                parsed = acc["account"]["data"]["parsed"]
                info = parsed["info"]
                mint = info["mint"]
                amount = float(info["tokenAmount"]["uiAmount"])
                symbol = TOKEN_SYMBOLS.get(mint, mint[:6] + "...")

                print(f"[SOLANA] Token {symbol} ({mint}) balance: {amount}")

                result["tokens"].append({
                    "symbol": symbol,
                    "mint": mint,
                    "amount": amount
                })
            except Exception as inner:
                print(f"[SOLANA] Token parse error: {inner}")
                continue

    except Exception as e:
        print(f"[SOLANA] Error for {address}: {e}")

    return result
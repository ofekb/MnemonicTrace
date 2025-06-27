import json
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

from config import SOLANA_RPC_URL

client = Client(SOLANA_RPC_URL)

TOKEN_SYMBOLS = {
    "Es9vMFrzaCERtPj1T6Q2kCezW4NB6C8Dw1JNKYfYzExv": "USDT",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8nndxrnbWgFLoXg": "USDC",
}

def process_seed(seed_phrase: str, max_addresses: int = 20):
    print("[SOLANA] Starting wallet derivation...")
    wallets = []

    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)

    for i in range(max_addresses):
        print(f"[SOLANA] Deriving address #{i}...")
        addr_ctx = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
        priv_key = addr_ctx.PrivateKey().Raw().ToHex()
        pub_addr = addr_ctx.PublicKey().ToAddress()

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

    print("[SOLANA] Done.")
    return wallets

def get_solana_wallet_info(address: str):
    result = {"SOL": 0.0, "tokens": []}
    try:
        # Get SOL balance
        sol = client.get_balance(Pubkey.from_string(address)).value / 1e9
        print(f"[SOLANA] SOL balance for {address}: {sol}")
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
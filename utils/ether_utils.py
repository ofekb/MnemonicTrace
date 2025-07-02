import time
from time import sleep

from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip32Slip10Secp256k1, EthAddr
import requests

from config import ETHERSCAN_API_KEY, INFURA_API_KEY
from wallet_profiles import WALLET_PROFILES

ERC20_TOKENS = [
    {"symbol": "USDT", "contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "decimals": 6},
    {"symbol": "USDC", "contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "decimals": 6}
]

def process_seed(seed_phrase, profile_name, address_depth=20, account_depth=5):
    print("[ETH] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    derivation_templates = WALLET_PROFILES.get(profile_name)

    if isinstance(derivation_templates, list):
        # Static profiles like MetaMask, TrustWallet
        for path_template in derivation_templates:
            for i in range(address_depth):
                path = path_template.replace("i", str(i))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    address = EthAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    print(f"[ETH] Deriving {path}...")

                    assets = []
                    if i != 0:
                        time.sleep(2)

                    eth_balance = get_eth_balance(address, ETHERSCAN_API_KEY, INFURA_API_KEY)
                    if float(eth_balance) > 0:
                        print(f"[ETH] ETH balance for {address}: {eth_balance}")
                        assets.append({"symbol": "ETH", "amount": eth_balance})
                    time.sleep(2)

                    token_balances = get_erc20_balances(address, ETHERSCAN_API_KEY)
                    if token_balances:
                        print(f"[ETH] ERC20 tokens for {address}: {token_balances}")
                    assets += token_balances

                    if assets:
                        wallets.append({
                            "network": "Ethereum",
                            "address": address,
                            "private_key": private_key,
                            "assets": assets
                        })
                except Exception as e:
                    print(f"[ETH] Error deriving {path}: {e}")
    else:
        # Dynamic profile like Ledger Live
        template = derivation_templates  # e.g., "m/44'/60'/{account}'/0/{index}"
        for account in range(account_depth):
            for index in range(address_depth):
                path = template.replace("{account}", str(account)).replace("{index}", str(index))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    address = EthAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    print(f"[ETH] Deriving {path}...")

                    assets = []
                    if index != 0:
                        time.sleep(2)

                    eth_balance = get_eth_balance(address, ETHERSCAN_API_KEY, INFURA_API_KEY)
                    if float(eth_balance) > 0:
                        print(f"[ETH] ETH balance for {address}: {eth_balance}")
                        assets.append({"symbol": "ETH", "amount": eth_balance})
                    time.sleep(2)

                    token_balances = get_erc20_balances(address, ETHERSCAN_API_KEY)
                    if token_balances:
                        print(f"[ETH] ERC20 tokens for {address}: {token_balances}")
                    assets += token_balances

                    if assets:
                        wallets.append({
                            "network": "Ethereum",
                            "address": address,
                            "private_key": private_key,
                            "assets": assets
                        })
                except Exception as e:
                    print(f"[ETH] Error deriving {path}: {e}")

    print("[ETH] Done.")
    return wallets


def get_eth_balance(address, etherscan_api_key, infura_api_key):
    try:
        if etherscan_api_key:
            url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={etherscan_api_key}"
            r = requests.get(url)
            result = int(r.json()["result"]) / 1e18
            return str(result)
        elif infura_api_key:
            headers = {'Content-Type': 'application/json'}
            data = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            r = requests.post(f"https://mainnet.infura.io/v3/{infura_api_key}", headers=headers, json=data)
            result = int(r.json()["result"], 16) / 1e18
            return str(result)
    except Exception as e:
        print(f"[ETH] Error getting ETH balance: {e}")
    return "0"

def get_erc20_balances(address, etherscan_api_key):
    balances = []
    if not etherscan_api_key:
        print("[ETH] Skipping ERC20 check (no API key)")
        return balances

    for token in ERC20_TOKENS:
        try:
            url = f"https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress={token['contract']}&address={address}&tag=latest&apikey={etherscan_api_key}"
            r = requests.get(url)
            raw = r.json()["result"]
            amount = int(raw) / (10 ** token["decimals"])
            if amount > 0:
                balances.append({"symbol": token["symbol"], "amount": str(amount)})
        except Exception as e:
            print(f"[ETH] Error checking {token['symbol']}: {e}")
    return balances

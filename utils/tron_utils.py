from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip32Slip10Secp256k1, TrxAddr
from tronpy.exceptions import AddressNotFound
import time

from tronpy.providers import HTTPProvider
from tronpy import Tron

from config import TRONGRID_API_KEY
from wallet_profiles import WALLET_PROFILES

provider = HTTPProvider(api_key=TRONGRID_API_KEY)
client = Tron(provider=provider)


TRC20_TOKENS = {
    "USDT": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
    "USDC": "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8"
    # Add more tokens only if they have public ABI and are verified
}

def process_seed(seed_phrase, profile_name, address_depth=20, account_depth=5):
    print("[TRON] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    derivation_templates = WALLET_PROFILES.get(profile_name)

    if not derivation_templates:
        print(f"[TRON] No derivation paths found for profile: {profile_name}")
        return wallets

    if isinstance(derivation_templates, list):
        # Static paths
        for path_template in derivation_templates:
            for i in range(address_depth):
                path = path_template.replace("i", str(i))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    tron_address = TrxAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    print(f"[TRON] Deriving {path}...")

                    assets = []

                    trx_balance = get_trx_balance(tron_address)
                    if float(trx_balance) > 0:
                        print(f"[TRON] TRX balance for {tron_address}: {trx_balance}")
                        assets.append({"symbol": "TRX", "amount": trx_balance})

                    trc20 = get_trc20_balances(tron_address)
                    if trc20:
                        print(f"[TRON] TRC20 tokens for {tron_address}: {trc20}")
                    assets += trc20

                    if assets:
                        wallets.append({
                            "network": "Tron",
                            "address": tron_address,
                            "private_key": private_key,
                            "assets": assets
                        })

                except Exception as e:
                    print(f"[TRON] Error processing {path}: {e}")
                time.sleep(0.3)

    else:
        # Dynamic path like Ledger
        template = derivation_templates  # e.g., "m/44'/195'/{account}'/0/{index}"
        for account in range(account_depth):
            for index in range(address_depth):
                path = template.replace("{account}", str(account)).replace("{index}", str(index))
                try:
                    addr = Bip32Slip10Secp256k1.FromSeed(seed_bytes).DerivePath(path)
                    tron_address = TrxAddr.EncodeKey(addr.PublicKey().KeyObject())
                    private_key = addr.PrivateKey().Raw().ToHex()

                    print(f"[TRON] Deriving {path}...")

                    assets = []

                    trx_balance = get_trx_balance(tron_address)
                    if float(trx_balance) > 0:
                        print(f"[TRON] TRX balance for {tron_address}: {trx_balance}")
                        assets.append({"symbol": "TRX", "amount": trx_balance})

                    trc20 = get_trc20_balances(tron_address)
                    if trc20:
                        print(f"[TRON] TRC20 tokens for {tron_address}: {trc20}")
                    assets += trc20

                    if assets:
                        wallets.append({
                            "network": "Tron",
                            "address": tron_address,
                            "private_key": private_key,
                            "assets": assets
                        })

                except Exception as e:
                    print(f"[TRON] Error processing {path}: {e}")
                time.sleep(0.3)

    print("[TRON] Done.")
    return wallets

def get_trx_balance(address):
    try:
        return str(client.get_account_balance(address))
    except AddressNotFound:
        return "0"
    except Exception as e:
        print(f"[TRON] Error getting TRX balance for {address}: {e}")
        return "0"

def get_trc20_balances(address):
    balances = []
    for symbol, contract_address in TRC20_TOKENS.items():
        try:
            contract = client.get_contract(contract_address)
            raw = contract.functions.balanceOf(address)
            decimals = contract.functions.decimals()
            amount = raw / (10 ** decimals)
            if amount > 0:
                balances.append({"symbol": symbol, "amount": str(amount)})
        except Exception as e:
            print(f"[TRON] Skipping {symbol} for {address} - {e}")
    return balances

# print(get_trc20_balances('THUPnrqoArCiUb4hdEoF5cbQhFqd7CnN6y'))

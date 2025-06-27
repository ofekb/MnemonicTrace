from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from tronpy.exceptions import AddressNotFound
import time

from tronpy.providers import HTTPProvider
from tronpy import Tron

from config import TRONGRID_API_KEY

provider = HTTPProvider(api_key=TRONGRID_API_KEY)
client = Tron(provider=provider)


TRC20_TOKENS = {
    "USDT": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
    "USDC": "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8"
    # Add more tokens only if they have public ABI and are verified
}

def process_seed(seed_phrase):
    print("[TRON] Starting derivation and balance check...")
    wallets = []
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip_obj = Bip44.FromSeed(seed_bytes, Bip44Coins.TRON)

    for i in range(20):
        print(f"[TRON] Deriving address #{i}...")
        try:
            addr = bip_obj.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
            tron_address = addr.PublicKey().ToAddress()
            private_key = addr.PrivateKey().Raw().ToHex()

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
            print(f"[TRON] Error processing address #{i}: {e}")

        time.sleep(0.3)  # prevent rate-limit

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

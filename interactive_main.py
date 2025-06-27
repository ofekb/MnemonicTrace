import os
import json
from utils import btc_utils, ether_utils, bnb_utils, sol_utils, tron_utils, xrp_utils
from logger import log_info, log_error, log_success
from helpers import load_seeds_from_file, get_seeds_from_input
import inquirer

networks_map = {
    "Bitcoin": btc_utils,
    "Ethereum": ether_utils,
    "BNB": bnb_utils,
    "Solana": sol_utils,
    "Tron": tron_utils,
    "XRP": xrp_utils
}

def choose_input_method():
    question = [
        inquirer.List("method", message="Choose input method", choices=["Enter manually", "Load from file"])
    ]
    answer = inquirer.prompt(question)
    if answer["method"] == "Enter manually":
        return get_seeds_from_input()
    else:
        return load_seeds_from_file()

def choose_networks():
    question = [
        inquirer.Checkbox("networks", message="Select networks to scan", choices=list(networks_map.keys()))
    ]
    return inquirer.prompt(question)["networks"]

def choose_btc_address_types():
    question = [
        inquirer.Checkbox(
            "types",
            message="Select Bitcoin address types to scan",
            choices=["legacy", "p2sh", "bech32", "taproot"]
        )
    ]
    answer = inquirer.prompt(question)
    return answer["types"] if answer else []


def choose_output_format():
    question = [
        inquirer.List("format", message="Choose output format", choices=["json", "txt"])
    ]
    return inquirer.prompt(question)["format"]

def choose_output_filename():
    question = [
        inquirer.Text("filename", message="Enter output file name (without extension)")
    ]
    return inquirer.prompt(question)["filename"]

def main():
    log_info("Welcome to the MnemonicTrace!")
    seeds = choose_input_method()
    networks = choose_networks()

    btc_address_types = choose_btc_address_types() if "Bitcoin" in networks else []
    if "Bitcoin" in networks and not btc_address_types:
        log_info("[BTC] No address types selected, skipping Bitcoin.")
        networks.remove("Bitcoin")

    output_format = choose_output_format()
    filename = choose_output_filename()

    results = []

    for seed in seeds:
        log_info(f"Processing seed: {seed[:8]}...")

        for net in networks:
            try:
                util = networks_map[net]

                if net == "Bitcoin":
                    result = util.process_seed(seed, btc_address_types)
                else:
                    result = util.process_seed(seed)

                if result:
                    for entry in result:
                        log_success(f"[{net}] Found {entry}")
                        results.append({
                            "network": net,
                            **entry
                        })
                else:
                    log_info(f"[{net}] No assets found")

            except Exception as e:
                if net == "XRP" and "account_data" in str(e):
                    log_info(f"[{net}] Account not found.")
                else:
                    log_error(f"[{net}] Error: {str(e)}")

    full_filename = f"{filename}.{output_format}"
    with open(full_filename, "w") as f:
        if output_format == "json":
            json.dump(results, f, indent=2)
        else:
            for entry in results:
                f.write(f"Network: {entry['network']}\n")
                f.write(f"Address: {entry.get('address', 'N/A')}\n")
                f.write(f"Balance: {entry.get('balance', 'N/A')}\n")
                f.write(f"Private Key: {entry.get('private_key', 'N/A')}\n")
                f.write("-" * 40 + "\n")

    log_success(f"Results saved to: {full_filename}")

if __name__ == "__main__":
    main()

WALLET_PROFILES = {
    # Shared ETH/BNB profiles
    "Standard (MetaMask / TrustWallet / Trezor / Exodus / Coinbase)": [
        "m/44'/60'/0'/0/i"
    ],

    "Ledger Live (Ethereum/BNB)": "m/44'/60'/{account}'/0/{index}",

    # Bitcoin
    "Standard (BTC BIP44)": [
        "m/44'/0'/0'/0/i"
    ],
    "Ledger Live (BTC)": "m/44'/0'/{account}'/0/{index}",

    # Solana
    "Standard (Phantom)": [
        "m/44'/501'/0'/0/i"
    ],
    "Ledger Live (Solana)": "m/44'/501'/{account}'/0/{index}",

    # TRON
    "Standard (TronLink)": [
        "m/44'/195'/0'/0/i"
    ],
    "Ledger Live (Tron)": "m/44'/195'/{account}'/0/{index}",

    # XRP
    "Standard (XUMM)": [
        "m/44'/144'/0'/0/i"
    ],
    "Ledger Live (XRP)": "m/44'/144'/{account}'/0/{index}"
}

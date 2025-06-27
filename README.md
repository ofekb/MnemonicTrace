# 🧠 MnemonicTrace Tool

Welcome to the **MnemonicTrace** – a powerful cross-chain seed scanner designed to recover and audit cryptocurrency wallets using a 12 or 24-word BIP39 seed phrase.

This tool is perfect for:
- 🔐 Wallet recovery attempts
- 🧪 Security auditing
- 🧭 Cross-chain balance verification

---

## 🚀 Features

✅ Supports multiple blockchains:
- Bitcoin (BTC)
- Ethereum (ETH)
- Binance Smart Chain (BNB)
- Solana (SOL)
- TRON (TRX)
- Ripple (XRP)

✅ Interactive CLI – easy-to-use wizard with step-by-step interface  
✅ Choose networks, seed input method, and output format  
✅ Human-readable logs with color-coded messages  
✅ Exports results to JSON or TXT  
✅ Works on macOS, Windows, and Linux  
✅ Offline-capable and self-contained

---

## 🛠 Installation & Usage

### 🖥 macOS / Linux

```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

### 🪟 Windows

Double-click `install_and_run.bat`  
_or from CMD:_
```cmd
install_and_run.bat
```

---

## 📘 How to Use the Tool (Step by Step)

When you launch the tool, you'll be guided through a series of menus:

1. **Seed Input**
   - `Enter manually` → Type/paste your 12 or 24 word seed (one or more)
   - `Load from file` → Use a `.txt` file with one seed per line

2. **Select Networks**
   - Use the **spacebar** to select or deselect networks
   - Press **Enter** when done to proceed

3. **Choose Output Format**
   - `json` → Machine-readable
   - `txt` → Human-friendly report

4. **Choose Output Filename**
   - Provide a name without extension (e.g., `my_results`)

The tool will then derive addresses, check balances, and export the results to your chosen format.

---

## 🧭 Keyboard Controls

| Action | Key |
|--------|-----|
| Select/Deselect option | `SPACE` |
| Confirm/Continue       | `ENTER` |
| Navigate menus         | `↑ / ↓` |

---

## 📂 Project Structure

| File / Folder | Description |
|---------------|-------------|
| `interactive_main.py` | The main user interface – interactive wizard |
| `install_and_run.sh` | Full auto-installer for macOS/Linux |
| `install_and_run.bat` | Full auto-installer for Windows |
| `requirements.txt` | Python dependencies |
| `run.command` | Optional Mac launcher |
| `config.py` | Your API keys and RPC endpoints |
| `utils/` | Network-specific wallet handling code |
| `logger.py` | Colorful logging helper |
| `helpers.py` | Utility functions (e.g. seed loading) |

---

## 📦 Output Example (TXT)

```
Network: Ethereum
Address: 0x123...abc
Balance: 0.314 ETH
Private Key: xxxxxxx...

----------------------------------------

Network: TRON
Address: TABC...
Balance: 4820 USDT
Private Key: xxxxxxx...
```

---


## 🔑 API Key Configuration

To enable balance lookups on supported networks, you must configure the following API keys and endpoints inside `config.py`:

```python
# config.py

# Ethereum / BSC
ETHERSCAN_API_KEY = "your_etherscan_api_key"
INFURA_API_KEY = "your_infura_api_key"
BSCSCAN_API_KEY = "your_bscscan_api_key"

# TRON
TRONSCAN_API_KEY = "your_tronscan_api_key"

# XRP
XRPL_API_ENDPOINT = "https://s1.ripple.com:51234"  # Default public endpoint (no key needed)

# Solana
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"  # Public RPC URL
```

You can register and obtain free API keys here:
- 🌐 https://etherscan.io/myapikey
- 🌐 https://bscscan.com/myapikey
- 🌐 https://tronscan.org (generate personal API key under developer settings)

📍 After getting the keys, open `config.py` and paste your keys in the correct places.  
Without valid API keys, some networks may fail to fetch balances or data.
---
## 🔐 Security Notes

- This tool **does not** upload any data online.
- Runs fully offline and locally.
- Use only for educational, research, or wallet recovery purposes.


---

## 📩 Support

Built by **Ofek Ben Harosh**  
Need help or want to improve the tool? You're welcome to reach out.


---


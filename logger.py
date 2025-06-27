from colorama import init, Fore

init(autoreset=True)

def log_info(msg):
    print(Fore.CYAN + "[INFO] " + msg)

def log_success(msg):
    print(Fore.GREEN + "[SUCCESS] " + msg)

def log_error(msg):
    print(Fore.RED + "[ERROR] " + msg)

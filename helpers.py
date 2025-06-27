def load_seeds_from_file():
    file = input("Enter path to file with seeds: ").strip()
    with open(file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_seeds_from_input():
    seeds = []
    print("Enter seeds (empty line to finish):")
    while True:
        line = input("> ").strip()
        if not line:
            break
        seeds.append(line)
    return seeds

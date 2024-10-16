import subprocess

# Chain configuration
CHAIN_CONFIG = {
    'arbitrum-sepolia': {'rpc': 'arbitrum-sepolia'},
    'bartio': {'rpc': 'bartio'},
    'imola': {'rpc': 'imola'},
    'local': {'rpc': 'local'}
}

def get_valid_input(prompt, validator, allow_multiple=False):
    while True:
        try:
            user_input = input(prompt)
            if allow_multiple:
                return [validator(item.strip()) for item in user_input.split(',')]
            return validator(user_input)
        except ValueError as e:
            print(f"Error: {e}")

def validate_chain(chain):
    if chain not in CHAIN_CONFIG:
        raise ValueError(f"Invalid chain. Choose from: {', '.join(CHAIN_CONFIG.keys())}")
    return chain

def validate_address(address):
    if not address.startswith('0x') or len(address) != 42:
        raise ValueError("Invalid Ethereum address format")
    return address

def validate_verbosity(level):
    if level not in ['v', 'vv', 'vvv', 'vvvv']:
        raise ValueError("Verbosity must be v, vv, vvv, or vvvv")
    return level

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print("Command output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code {e.returncode}")
        print(e.output)

def main():
    chains = get_valid_input(f"Enter CHAIN_NAME(s) ({', '.join(CHAIN_CONFIG.keys())}), comma-separated for multiple: ", validate_chain, allow_multiple=True)
    verbosity = get_valid_input("Enter verbosity level (v, vv, vvv, vvvv): ", validate_verbosity)
    broadcast = input("Do you want to broadcast? (y/n): ").lower() == 'y'

    for chain in chains:
        feed_address = get_valid_input(f"Enter FEED_ADDRESS for {chain}: ", validate_address)

        command = f"""source .env && forge script\\
    --rpc-url {CHAIN_CONFIG[chain]['rpc']}\\
    scripts/CreateMarketAndTest.s.sol:CreateMarketAndTest\\
    {chain}\\
    {feed_address}\\
    --sig 'run(string,address)'\\
    -{verbosity}"""

        if broadcast:
            command += " --broadcast"
        
        print(f"\nCommand for chain {chain}:")
        print(command)
        
        execute = input("Do you want to execute this command? (y/n): ").lower()
        if execute == 'y':
            execute_command(command)
        else:
            print("Command not executed.")

if __name__ == "__main__":
    main()
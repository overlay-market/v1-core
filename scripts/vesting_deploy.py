from brownie import project, accounts, config

DAI_ADDRESS = "0x332C7aC34580dfEF553B7726549cEc7015C4B39b"

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def main():
    """
        Deploys a vesting vault contract and create vesting for a address
    """
    VestingVault = project.load(config["dependencies"][2]).VestingVault
    IERC20 = project.load(config["dependencies"][0]).IERC20
    account = accounts[0]
    vesting_vault = VestingVault.deploy(DAI_ADDRESS, 2, {"from": account}, publish_source=True)

    vesting_vault.initalize(account.address, account.address)

    DAI = IERC20.at(DAI_ADDRESS)

    DAI.approve(vesting_vault.address, 1000000e18, {"from": account})

    vesting_vault.deposit(1000000e18, {"from": account})

    vesting_vault.addGrantAndDelegate(account.address, 10000e18, 0, 7549180, 7549100, ZERO_ADDRESS)



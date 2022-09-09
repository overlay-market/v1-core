from brownie import project, accounts, config

DAI_ADDRESS = "0x332C7aC34580dfEF553B7726549cEc7015C4B39b"

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def main():
    """
        Deploys a vesting vault contract and create vesting for a address
    """
    VestingVaultProject = project.load(config["dependencies"][2])
    VestingVault = VestingVaultProject.VestingVault
    ERC20 = project.load(config["dependencies"][0]).ERC20

    account = accounts[0]
    vesting_vault = VestingVault.deploy(
        DAI_ADDRESS, 2, {"from": account}, publish_source=True)

    vesting_vault.initialize(
        account.address, account.address, {"from": account})

    DAI = ERC20.at(DAI_ADDRESS)

    DAI.approve(vesting_vault.address, 1000000e18, {"from": account})

    vesting_vault.deposit(1000000e18, {"from": account})

    vesting_vault.addGrantAndDelegate(
        account.address, 10000e18, 0, 7553250, 7553150, ZERO_ADDRESS, {"from": account})

import click

from brownie import OverlayV1UniswapV3Factory, accounts, network


UNIV3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"


def main():
    """
    Deploys a new OverlayV1UniswapV3Factory contract, which allows for
    permissionless deployment of OverlayV1UniswapV3Feed feeds.
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # assemble constructor params
    params = ["ovl (address)", "uniV3Factory (address)",
              "microWindow (uint256)", "macroWindow (uint256)",
              "observationCardinalityMinimum (uint16)",
              "averageBlockTime (uint256)"]
    args = [
        click.prompt(f"{param}")
        if param != "uniV3Factory (address)"
        else UNIV3_FACTORY
        for param in params
    ]

    # deploy feed factory
    feed_factory = OverlayV1UniswapV3Factory.deploy(
        *args, {"from": dev}, publish_source=True)
    click.echo(f"Uniswap V3 Feed Factory deployed [{feed_factory.address}]")
    click.echo("NOTE: Feed Factory is not registered in OverlayV1Factory yet!")

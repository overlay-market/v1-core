import click

from brownie import accounts, network, Contract

def main():
    """
    Deploys a new OverlayV1ChainlinkFeed contract, and actual market 
    from OverlayV1Factory contract
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    # assemble feed constructor param
    feed_args = [click.prompt("_aggregator")]

    # get overlay v1 chainlink feed factory address
    overlay_v1_chainlink_feed_factory_contract_address = click.prompt(
        "OverlayV1ChainlinkFeedFactoryAddress")

    overlay_v1_chainlink_feed_factory_contract = Contract.from_explorer(
        f"{overlay_v1_chainlink_feed_factory_contract_address}")

    # get feed address
    feed = overlay_v1_chainlink_feed_factory_contract.deployFeed.call(
        *feed_args, {"from": dev})

    # deploy feed
    overlay_v1_chainlink_feed_factory_contract.deployFeed(
        *feed_args, {"from": dev})
    click.echo(f"Chainlink Feed deployed [{feed}]")

    """
    About to start testing this part
    """

    # assemble market constructor params
    # params = ["feedFactory (address)", "feed (address)", "params (uint256[15])"]

    # market_args = [
    #     click.prompt(f"{param}")
    #     if param != "feed (address)"
    #     else feed
    #     for param in params
    # ]

    # # get overlay v1 factory address
    # overlay_v1_factory_address = [click.prompt(
    #     "OverlayV1Factory")]

    # # deploy maket
    # overlay_v1_factory_contract = Contract.from_explorer(
    #     f'{overlay_v1_factory_address}')

    #  # get market address
    # market = overlay_v1_factory_contract.deployMarket.call(
    #     *market_args, {"from": dev})

    # # deploy market
    # feed = overlay_v1_factory_contract.deployMarket.call(
    #     *market_args, {"from": dev})

    # click.echo(f"Market deployed [{market}]")

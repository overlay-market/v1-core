from brownie import accounts
from scripts.feeds.chainlink import deployFeed as df
from scripts.feeds.chainlink import deployMarket as dm


def main(acc, chain_id):
    dev = accounts.load(acc)
    df.main(dev, chain_id)
    dm.main(dev, chain_id)

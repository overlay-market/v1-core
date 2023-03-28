from scripts.feeds.chainlink import deployFeed as df
from scripts.feeds.chainlink import deployMarket as dm

def main(acc, chain_id):
    df.main(acc, chain_id)
    dm.main(acc, chain_id)

from scripts.feeds.chainlink import deployFeed as df
from scripts.feeds.chainlink import deployMarket as dm

def main():
    df.main()
    dm.main()

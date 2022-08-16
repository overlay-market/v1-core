import click
from brownie import \
    OverlayV1Portal, \
    accounts, \
    network


def main():

  dev = accounts.load(click.prompt(
    "Account", type=click.Choice(accounts.load())))

  defaults = {"from": dev}

  orig_portal = OverlayV1Portal.at(
    click.prompt("Origin Portal", type=str))

  dest_chain_id = click.prompt("Destination Chain ID", type=int)
  dest_portal = click.prompt("Destination Portal", type=str)

  set_tx = orig_portal.setTrustedRemote(dest_chain_id, 
      dest_portal, defaults)
  

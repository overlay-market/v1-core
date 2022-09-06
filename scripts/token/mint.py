import click
import sys
import ape_safe
from ape_safe import ApeSafe
from dotenv import dotenv_values
from importlib_metadata import version

from brownie import OverlayV1Token, accounts, network, web3

def main():
  """ Mints tokens to an arbitrary address """

  gov = dotenv_values()['GOVERNANCE']

  safe = ApeSafe(gov)

  dev = accounts.load(click.prompt(
    "Account", type=click.Choice(accounts.load())))

  to = "0xA600AdF7CB8C750482a828712849ee026446aA66"

  # Must have a checksummed address
  ovl = safe.contract("0xfa474A313BDBF69E287dbef667e2f626ea2574Df")

  amt = 1e18

  print(network.show_active())

  ovl.mint(to, amt)

  print(safe.ethereum_client)

  safe_tx = safe.multisend_from_receipts()
  safe.preview(safe_tx)
  safe.post_transaction(safe_tx)


import click
from brownie import \
    OverlayV1Token, \
    OverlayV1Portal, \
    accounts, \
    network

rinkeby_endp = "0x79a63d6d8BBD5c6dfc774dA79bCcD948EAcb53FA"
rinkeby_chain_id = 10001
op_kovan_endp = "0x72aB53a133b27Fa428ca7Dc263080807AfEc91b5"
op_kovan_chain_id = 10011
mumbai_endp = "0xf69186dfBa60DdB133E91E9A4B5673624293d8F8"
mumbai_chain_id = 10009

def main():
  
  dev = accounts.load(click.prompt(
    "Account", type=click.Choice(accounts.load())))

  layer_zero_endpoint = click.prompt("Layer Zero Endpoint", type=str)

  defaults = {"from": dev}

  ovl = OverlayV1Token.deploy(defaults)
  print("OVL deployed at:", ovl.address)

  portal = OverlayV1Portal.deploy(
      ovl, layer_zero_endpoint, defaults);
  print("Portal deployed at:", portal.address)

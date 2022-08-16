import click
from brownie import \
    OverlayV1Token, \
    OverlayV1Portal, \
    accounts, \
    convert, \
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

  defaults = {"from": dev}

  orig_portal = OverlayV1Portal.at(
      click.prompt("Originating Portal", type=str))

  dest_chain_id = click.prompt("Destination Chain Id", type=int)
  dest_portal = click.prompt("Destination Portal Address", type=str)

  est = orig_portal.estimateFees(
      dest_chain_id,
      dest_portal,
      orig_portal.conjure.encode_input(dev, 5e18),
      False,
      convert.to_bytes("","bytes")
  )

  amount = convert.datatypes.Wei(est[0])

  print("amount", amount)

  try:
    dpstch = orig_portal.dispatch(
        dest_chain_id,
        dest_portal,
        5e18,
        { "from": dev,
          "gas_limit": 300000,
          "allow_revert": True,
          "amount": amount })

    print("dpstch", dpstch)
  except Exception as e:
    print(e)

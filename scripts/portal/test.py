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

  print("hello")
  
  dev = accounts.load('pilot')

  defaults = {"from": dev}

  print("dev", dev)


  

  to = "0xA600AdF7CB8C750482a828712849ee026446aA66"

  rinkeby_ovl = OverlayV1Token.deploy(defaults)

  rinkeby_portal = OverlayV1Portal.deploy(
      rinkeby_ovl, rinkeby_endp, defaults);

  network.disconnect()
  network.connect('polygon-test')

  mumbai_ovl = OverlayV1Token.deploy(defaults)

  mumbai_portal = OverlayV1Portal.deploy(
      mumbai_ovl, mumbai_endp, defaults);






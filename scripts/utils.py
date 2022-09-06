from brownie import web3

def role(name):
    if name == "ADMIN":
        return HexBytes("0x00")
    return web3.solidityKeccak(['string'], [name])

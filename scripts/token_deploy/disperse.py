import click

from brownie import OverlayV1Token, accounts, network, web3, interface
from hexbytes import HexBytes

RECIPIENTS = [
  "0x2a2e181cc177974c5d013240c34e1def1a3cc31a",
  "0x530f09ea449f3f84b74f42d5ea82aecdb82f9613",
  "0x483d25d45518ef52e4083284faefeba702b6ad35",
  "0x5b9950c198aa3e2ef0a8d0c1c640b6b13c3ef216",
  "0x36c8e1aabb2008e443fc10115902d1d336a38864",
  "0x716e3f2f257c9956b56842a67f14e623e7629053",
  "0x19dfdc194bb5cf599af78b1967dbb3783c590720",
  "0x3b25abf8e157fa75bbc22ba91c47c7507f6988fb",
  "0xfaf6bb8f1a300130fb9dc582dc8363a50841882d",
  "0x26d4068157ee21536d39b8de38f0ccb8e08c9cfb",
  "0x28829cdb803c41cb8a7858455b4ffc70b5dfacf4",
  "0x339ae9545e7e1470f1dac54eed56afb6e1377d2f",
  "0x7a198392a9fd3b24cd6f3cbf9f15ed48269c8fcf",
  "0xac5fcbed890eeeaabe00f1aa5a79e6ab252cc278",
  "0xb2e89a8f93cedcfae23304a3615a64feb0e02514",
  "0xe5cc7b86bb776f9ceaad80e6d9e1ceb6ab48bb7c",
  "0xd6f1875bc1b9d0e8bcec7da22a22bdb359082ae7",
  "0xe421b5c6680bb06f25e0f8dd138c96913d2c1599",
  "0xef1c68fb74782a63ca676e39887925bf38736ed6",
  "0xf9107317b0ff77ed5b7adea15e50514a3564002b",
  "0x46376cf0ef9bd3daafab1b57e6c939b3062c2af1",
  "0x51f4e96abf315ec7597cb56d89637455ebf60f4e",
  "0x608f0cade420e14b35b6f494867f302e78149d8a",
  "0x672c3b982325be86e221fe5d0eb5391ffa9cc8fc",
  "0x6a846300b7168106e30929ce1fa42148cbd9f4a9",
  "0x6bcfe7307663bb2b0c1c70294c8af1ea01fef0de",
  "0x703830e346936cb73fbbcfac3b543c1621a9d3f8",
  "0x05fd601cc84aeed9b6e378aac9d46ed801d38069",
  "0x0f97b7ff167be3dbeda03389320726547463bc84",
  "0x84624fb8b703da691f6b84c559990ff35b718861",
  "0x86d95ad7b3396bfdbbd46b0c9804f3a8e91a0607",
  "0x8a3084ad2e8b04d316e95fca3ff49af4bc4e784b",
  "0x8e3862fb8e38220e65aa07f86f63098f4e84bca6",
  "0x9adfd762d997bd382028a579bb68bdd49d97493c",
  "0x9e42997109143decea3a2cf0b1dd8204c69aca86",
  "0xaa21505a90f5a5d1e40c39bd719f1b3bef843cbc",
  "0x15d3e6478f91f12cc0f5d8c53daf32f6e4ab1f2c",
  "0xb191eeaf7ffed5bcbe5febdeaae562d753e6c5cb",
  "0x1cae141ec4f5becd042d8df35e397b00c26e0e8a",
  "0xc7efca3ce6f7ea4be3d3ee4aae241d8b7dd9a6fe",
  "0xca77380d0caa2d2eb484a4c0c92926764ca9587b",
  "0x1d1569e8ecb88c0cb35f8920649f1aa66173a8bc",
  "0x356b0c093e663eb73970255f911ad5909e7fe4e8",
  "0xdc826ac58a5fa9f4f35aad8ad6b679fa2f9fd6dd",
  "0xdfb27231979a3367579794001c006f6d3875d16f",
  "0x22c17332f5527703d34121704c036d713418c232",
  "0xe4518c427b210e950bb1cfb207e04d9af60f919a",
  "0x77e8ab134f6d6f7309e6f565d82456b63723f506",
  "0xe5daaaf9e1c605eb5087b9483e7ea190597579ab",
  "0xecbe3854b26750b301341bad149185e55544aba1",
  "0x3a400d822e1e9cc7f8b34abea0ae77de99d45eb3",
  "0xf4905bd17982966bb4bb5faac8cd117be8a59ef6",
  "0x3c984f08981653a6b049983f4e31af162892d88a",
  "0xcdb2de3c7e3523f943904bdaab94e316853601ee"
]


DISPERSE = "0xD152f549545093347A162Dce210e7293f1452150"

ADMIN = "ADMIN"
MINTER = "MINTER"
def role(name):
    if name == ADMIN:
        return HexBytes("0x00")
    return web3.solidityKeccak(['string'], [name])


def main():
    """
    Deploys new OverlayV1Token and OverlayV1Factory contracts.

    Grants token admin rights to the factory to enable deploying of markets
    with mint and burn priveleges. Grants token admin rights to governor and
    renounces all token rights for deployer.
    """
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))

    disperse = getattr(interface, 'IDisperse')(DISPERSE)

    recipients = RECIPIENTS
    recipients += recipients + recipients
    values = [ 1e18 for i in range(len(recipients)) ]
    total = sum(values)

    # deploy OVL
    ovl = OverlayV1Token.deploy({"from": dev}, publish_source=True)
    click.echo(f"OVL Token deployed [{ovl.address}]")

    ovl.grantRole(role(MINTER), dev, {"from": dev})
    click.echo(f"Deployer address granted minting permissions")

    ovl.mint(dev, total, {'from': dev})
    click.echo(f"Minted {total} to deployer")

    ovl.approve(disperse, total, {'from': dev})
    click.echo(f"Disperse approved {total} for spending.")

    disperse.disperseToken(ovl, recipients, values, {'from': dev})
    click.echo(f"Dispersal accomplished.")



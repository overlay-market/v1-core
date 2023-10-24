from ape_safe import ApeSafe
from brownie import network, Contract, history, web3
from scripts.overlay_management import OM
from scripts import utils

# Add feed addresses corresponding to the markets that need to be removed
FEED_ADDRS = [
    '0x77Daa40022325B392d3c6757f95F4DF3B79Fc6e8'
    ]


def main(chain_id, grant_guardian_role=False):
    print(f"You are using the '{network.show_active()}' network")
    protocol_safe = OM.const_addresses[chain_id][OM.PROTOCOL_SAFE]
    safe = ApeSafe(protocol_safe)

    # Grant guardian role
    if grant_guardian_role:
        guardian_role = web3.solidityKeccak(['string'], ["GUARDIAN"])
        ovl = utils.load_const_contract(chain_id, OM.OVL_ADDRESS)
        ovl.grantRole(guardian_role, protocol_safe, {'from': safe.address})

    # Shutdown markets
    factory = utils.load_const_contract(chain_id, OM.FACTORY_ADDRESS)
    for feed_addr in FEED_ADDRS:
        tx = factory.shutdown(feed_addr, {'from': safe.address})

    # Sign and post
    hist = history.from_sender(safe.address)
    txs_to_sign = hist[-len(FEED_ADDRS)-1:] if grant_guardian_role else hist[-len(FEED_ADDRS):]
    print(f'Num txs to sign: {len(txs_to_sign)}')
    safe_tx = safe.multisend_from_receipts(txs_to_sign)
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)

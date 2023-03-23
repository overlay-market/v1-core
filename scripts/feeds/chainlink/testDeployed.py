from scripts.overlay_management import OM
from brownie import accounts, Contract
import numpy as np
from pytest import approx


def load_contract(address):
    try:
        return Contract(address)
    except ValueError:
        return Contract.from_explorer(address)


def get_prices(market, state):
    return state.prices(market)


def get_latest_from_feed(feed):
    return feed.latest()


def get_ois(market, state):
    return state.ois(market)


def approve_all_ovl_to_market(ovl, acc, market):
    bal = ovl.balanceOf(acc)
    ovl.approve(market, bal, {'from': acc})


def build(market, is_long, acc):
    price_limit = 2**256-1 if is_long else 0
    tx = market.build(1e17, 1e18, is_long, price_limit, {'from': acc})
    pid = tx.events['Build']['positionId']
    return pid


def unwind(market, is_long, pid, acc):
    price_limit = 0 if is_long else 2**256-1
    market.unwind(pid, 1e18, price_limit, {'from': acc})


def test_static_spread(prices, latest_feed, params):
    (bid, ask, _) = prices
    (_, _, _, price_micro, price_macro, _, _, _) = latest_feed
    expect_bid = int(
        min(price_micro, price_macro) * np.exp(-params['delta']/1e18)
    )
    expect_ask = int(
        max(price_micro, price_macro) * np.exp(-params['delta']/1e18)
    )
    assert expect_bid == approx(bid, rel=1e4)
    assert expect_ask == approx(ask, rel=1e4)


def test_params_equal(market, param_names, param_values):
    for i, v in enumerate(param_names):
        assert market.params(i) == param_values[v]


def test_impact(market, state, prices, params):
    lmbd = params['lambda']
    (bid, ask, mid) = prices
    oi = (10e18/mid) * 1e18  # Test with position of notional size 10 OVL
    frac_oi = state.fractionOfCapOi(market, oi)
    vol_ask = state.volumeAsk(market, frac_oi)
    actual_ask_w_impact = state.ask(market, frac_oi)
    expected_ask_w_impact = int(ask * np.exp((lmbd/1e18) * (vol_ask/1e18)))
    assert expected_ask_w_impact == approx(actual_ask_w_impact, rel=1e4)

    vol_bid = state.volumeBid(market, frac_oi)
    actual_bid_w_impact = state.bid(market, frac_oi)
    expected_bid_w_impact = int(bid * np.exp((lmbd/1e18) * (vol_bid/1e18)))
    assert expected_bid_w_impact == approx(actual_bid_w_impact, rel=1e4)


# def test_funding_rate(market, state):
#     k = PARAMS['k']
#     long_oi, short_oi = market.oiLong(), market.oiShort()
#     imb_oi = abs(long_oi - short_oi) * (-1 if short_oi > long_oi else 1)
#     total_oi = long_oi + short_oi
#     actual_funding_rate = state.fundingRate(market)

#     if total_oi == 0:
#         assert actual_funding_rate == 0
#     else:
#         expected_funding_rate = 2 * k * imb_oi/total_oi
#         assert expected_funding_rate == actual_funding_rate


def main(chain_id, market_id, oracle_id):
    # acc = accounts.load(acc)
    # Load all_feeds_all_parameters.json
    afap = OM.get_all_feeds_all_parameters()
    market_vars = afap[market_id][chain_id][oracle_id]
    
    # Load data from afap
    params = market_vars['risk_parameters']
    market = load_contract(market_vars['market'])
    feed = load_contract(market_vars['feed_address'])
    
    # Load addresses from class variables 
    ovl = load_contract(OM.const_addresses[chain_id]['ovl'])
    state = load_contract(OM.const_addresses[chain_id]['state'])

    # Get prices
    prices = get_prices(market, state)
    latest_feed = get_latest_from_feed(feed)

    # print(f'Amount OVL held by testing account: {ovl.balanceOf(acc)/1e18}')
    # print(f'Amount ETH held by testing account: {acc.balance()/1e18}')

    # Check if parameters input was correct while deploying contract
    test_params_equal(market, OM.risk_params, params)
    print('On-chain risk parameters as expected')

    # Check bid-ask static spread (delta)
    test_static_spread(prices, latest_feed, params)
    print('Static spread as expected')

    # Check impact (lambda)
    test_impact(market, state, prices, params)
    print('Market impact as expected')

    # # Check funding rate
    # test_funding_rate(market, state)
    # print('Funding rate as expected')

    # # Build position and check funding rate
    # approve_all_ovl_to_market(ovl, acc, market)
    # is_long = True
    # pid = build(market, is_long, acc)
    # test_funding_rate(market, state)
    # print('Funding rate after building position as expected')

    # # Unwind position and check funding rate
    # unwind(market, is_long, pid, acc)
    # test_funding_rate(market, state)
    # print('Funding rate after unwinding position as expected')
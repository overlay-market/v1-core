// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Run with:
// $ source .env
// $ forge script scripts/Create.s.sol:CreateMarketScript --rpc-url $RPC --verify -vvvv --broadcast

contract CreateMarketScript is Script {
    // TODO: update values as needed
    // NOTE: the periphery contracts should be deployed before running this script
    address constant FACTORY = 0xc10e8E06b1b8DADB8E94120650414AFfedD17aF9;
    address constant FEED_FACTORY = 0x0000000000000000000000000000000000000000;
    address constant FEED = 0x0000000000000000000000000000000000000000;
    uint256[15] MARKET_PARAMS = [
        uint256(122000000000), // k
        500000000000000000, // lmbda
        2500000000000000, // delta
        5000000000000000000, // capPayoff
        8e23, // capNotional
        5000000000000000000, // capLeverage
        2592000, // circuitBreakerWindow
        66670000000000000000000, // circuitBreakerMintTarget
        100000000000000000, // maintenanceMargin
        100000000000000000, // maintenanceMarginBurnRate
        50000000000000000, // liquidationFeeRate
        750000000000000, // tradingFeeRate
        1e14, // minCollateral
        25000000000000, // priceDriftUpperLimit
        250 // averageBlockTime
    ];

    function run() external {
        // NOTE: this should be the private key of the GOVERNOR
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        OverlayV1Factory factory = OverlayV1Factory(FACTORY);

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->
        
        address market = factory.deployMarket(FEED_FACTORY, FEED, MARKET_PARAMS);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Market deployed at:", market);
    }
}

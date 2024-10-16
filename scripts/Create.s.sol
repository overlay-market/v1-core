// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";
import {BartioConfig} from "scripts/config/Bartio.config.sol";
import {ImolaMovementConfig} from "scripts/config/ImolaMovement.config.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
// $ source .env
// $ source .env && forge script scripts/Create.s.sol:CreateMarketScript --rpc-url $RPC -vvvv --broadcast

// NOTE: the periphery contract should be deployed before running this script
contract CreateMarketScript is Script {
    // TODO: update values as needed
    address constant FEED = 0xf08ED11Ec4775BE0c90271276af7D07fafDE2eC7;
    uint256[15] MARKET_PARAMS = [
        uint256(55321048027), // k
        428000000000000000, // lmbda
        5900000000000000, // delta
        5000000000000000000, // capPayoff
        2000000000000000000000000, // capNotional
        10000000000000000000, // capLeverage
        2592000, // circuitBreakerWindow
        1667000000000000000000, // circuitBreakerMintTarget
        34240518999999996, // maintenanceMargin
        50000000000000000, // maintenanceMarginBurnRate
        50000000000000000, // liquidationFeeRate
        750000000000000, // tradingFeeRate
        100000000000000, // minCollateral
        15000000000000, // priceDriftUpperLimit
        250 // averageBlockTime
    ];

    function run() external {
        // NOTE: this should be the private key of the GOVERNOR
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        OverlayV1Factory factory = OverlayV1Factory(ImolaMovementConfig.V1_FACTORY);

        address deployedMarket = factory.getMarket(FEED);
        if (deployedMarket != address(0)) console2.log("market already deployed to:", deployedMarket);

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        address market = factory.deployMarket(ImolaMovementConfig.FEED_FACTORY, FEED, MARKET_PARAMS);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Market deployed at:", market);
    }
}

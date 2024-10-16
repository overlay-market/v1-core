// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1ChainlinkFeed} from "contracts/feeds/chainlink/OverlayV1ChainlinkFeed.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
// $ source .env
// $ forge script scripts/QueryMarketContract.s.sol:QueryMarketContract -vvvv --rpc-url $RPC --broadcast 

// NOTE: the periphery contract should be deployed before running this script
contract QueryMarketContract is Script {

    function run() external {
        // NOTE: this should be the private key of the GOVERNOR
        uint256 DEPLOYER_PK = vm.envUint("DEPLOYER_PK");

        OverlayV1Market market = OverlayV1Market(0xB021EB4489c230234567Ca6789e53403310Db090);
        // OverlayV1Factory factory = OverlayV1Factory(market.factory());
        // address sequencer = address(factory.sequencerOracle());

        // OverlayV1ChainlinkFeed feed = OverlayV1ChainlinkFeed(0x43429AECD659324e136429FdF23Ba11cE489FA9e);
        // console2.log("feed description:", feed.description());
        // console2.log("feed decimals:", feed.decimals());
        // console2.log("timestamp:", feed.latest().timestamp);
        console2.log("oiLong", market.oiLong());
        console2.log("oiShort:", market.oiShort());

        // vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        // factory.setSequencerOracle(0xB9A378CE9CDf3CD5c3ce79869008135a21aDc3A8);
        // uint256 posId = market.build(1e18, 1e18, true, 0);

        // <!-- END DEPLOYMENT -->

        // vm.stopBroadcast();

        // console2.log("Built position:", posId);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
/* 
    source .env && forge script\
    --rpc-url <CHAIN_NAME>\
    scripts/CreateMarketAndTest.s.sol:CreateMarketAndTest\
    <CHAIN_NAME>\
    <FEED_ADDRESS>\
    --sig 'run(string,address)'\
    -vvvv
*/
/* 
    source .env && forge script\
    --rpc-url imola\
    scripts/CreateMarketAndTest.s.sol:CreateMarketAndTest\
    imola\
    0xbfCBfd071B3c8C71baD14569A44cb5CE76330127\
    --sig 'run(string,address)'\
    -vvvv
*/

// NOTE: the periphery contract should be deployed before running this script
contract CreateMarketAndTest is Script {
    // TODO: update values as needed
    // address constant FEED = 0xf08ED11Ec4775BE0c90271276af7D07fafDE2eC7;
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

    function run(
        string calldata _network,
        address _feed
    ) external {
        // NOTE: this should be the private key of the GOVERNOR
        uint256 DEPLOYER_PK;
        // Select the correct DEPLOYER_PK based on the network
        if (compareStrings(_network, "local")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK");
        } else if (compareStrings(_network, "bartio")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK_BARTIO");
        } else if (compareStrings(_network, "berachain")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK");
        } else if (compareStrings(_network, "imola")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK_IMOLA");
        } else if (compareStrings(_network, "arbitrum-sepolia")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK_ARB_SEPOLIA");
        } else {
            revert("Unsupported network");
        }

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        address market_ = createMarket(_network, _feed, MARKET_PARAMS);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Market deployed at:", market_);
    }

    function createMarket(
        string memory _network, 
        address _feed,
        uint256[15] memory _marketParams
    ) internal returns(address market) {
        address v1FactoryAddress;
        address feedFactory;

        // Select the correct feedFactory address based on the network
        if (compareStrings(_network, "local")) {
            v1FactoryAddress = address(0);
            feedFactory = address(0);
        } else if (compareStrings(_network, "berachain")) {
            v1FactoryAddress = 0xc5F85207a16FB6634eAd4f17Ad5222F122e8F0De;
            feedFactory = 0x7A6F3ec4F70A3079d460e096A5e6373b30be6649;
        } else if (compareStrings(_network, "bartio")) {
            v1FactoryAddress = 0xBe048017966c2787f548De1Df5834449eC4c4f50;
            feedFactory = 0xc0dE47Cbb26C2e19B82f9E205b0b0FfcD7947290;
        } else if (compareStrings(_network, "imola")) {
            v1FactoryAddress = 0xb136c8f0EA9D1c3F676f91FeacEA8BF967fDA7d0;
            feedFactory = 0xef0cba735406Bc5F698656A8219Ff0d09EaB5d31;
        } else if (compareStrings(_network, "arbitrum-sepolia")) {
            v1FactoryAddress = 0xa2dBe262D27647243Ac3187d05DBF6c3C6ECC14D;
            feedFactory = 0x21a84b9a5b746Fe85e13f11E745960DBEdB247B1;
        } else {
            revert("Unsupported network");
        }

        OverlayV1Factory factory = OverlayV1Factory(v1FactoryAddress);

        // check if market is already deployed
        {
            address deployedMarket = factory.getMarket(_feed);
            if (deployedMarket != address(0)) console2.log("market already deployed to:", deployedMarket);
        }

        market = factory.deployMarket(feedFactory, _feed, _marketParams);
    }

    function compareStrings(string memory a, string memory b) public pure returns (bool) {
        return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
    }
}

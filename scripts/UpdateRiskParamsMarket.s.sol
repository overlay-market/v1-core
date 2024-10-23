// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {OverlayV1Factory} from "contracts/OverlayV1Factory.sol";
import {OverlayV1Market} from "contracts/OverlayV1Market.sol";
import {ArbSepoliaConfig} from "scripts/config/ArbSepolia.config.sol";
import {ArbMainnetConfig} from "scripts/config/ArbMainnet.config.sol";
import {BartioConfig} from "scripts/config/Bartio.config.sol";
import {ImolaMovementConfig} from "scripts/config/ImolaMovement.config.sol";
import "contracts/libraries/Risk.sol";

// 1. Set required environment variables: ETHERSCAN_API_KEY, DEPLOYER_PK, RPC.
// 2. Update the config file for the network you are deploying to.
// 3. Run with:
/* 
    source .env && forge script\
    --rpc-url <CHAIN_NAME>\
    scripts/UpdateRiskParamsMarket.s.sol:UpdateRiskParamsMarket\
    <CHAIN_NAME>\
    <FEED_ADDRESS>\
    --sig 'run(string,address)'\
    -vvvv
*/
/* 
    source .env && forge script\
    --rpc-url imola\
    scripts/UpdateRiskParamsMarket.s.sol:UpdateRiskParamsMarket\
    imola\
    0x5322bd48Cefe38B1e65DE61D65a160eA40FA56CA\
    --sig 'run(string,address)'\
    -vvvv --broadcast
*/

// NOTE: the periphery contract should be deployed before running this script
contract UpdateRiskParamsMarket is Script {
    using Risk for uint256[15];

    uint256[15] MARKET_PARAMS = [
        uint256(116000000000), // k
        70000000000000008, // lmbda
        1600000000000000, // delta
        5000000000000000000, // capPayoff
        2000000000000000000000000, // capNotional
        20000000000000000000, // capLeverage
        2592000, // circuitBreakerWindow
        1667000000000000000000, // circuitBreakerMintTarget
        40000000000000000, // maintenanceMargin
        50000000000000000, // maintenanceMarginBurnRate
        50000000000000000, // liquidationFeeRate
        750000000000000, // tradingFeeRate
        100000000000000, // minCollateral
        87000000000000, // priceDriftUpperLimit
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
        } else if (compareStrings(_network, "imola")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK_IMOLA");
        } else if (compareStrings(_network, "arbitrum-sepolia")) {
            DEPLOYER_PK = vm.envUint("DEPLOYER_PK_ARB_SEPOLIA");
        } else {
            revert("Unsupported network");
        }

        vm.startBroadcast(DEPLOYER_PK);

        // <!---- START DEPLOYMENT ---->

        address market_ = updateRiskParamsMarket(_network, _feed, MARKET_PARAMS);

        // <!-- END DEPLOYMENT -->

        vm.stopBroadcast();

        console2.log("Market updated at:", market_);
    }

    function updateRiskParamsMarket(
        string memory _network, 
        address _feed,
        uint256[15] memory _marketParams
    ) internal returns(address) {
        address v1FactoryAddress;

        // Select the correct feedFactory address based on the network
        if (compareStrings(_network, "local")) {
            v1FactoryAddress = address(0);
        } else if (compareStrings(_network, "bartio")) {
            v1FactoryAddress = 0xBe048017966c2787f548De1Df5834449eC4c4f50;
        } else if (compareStrings(_network, "imola")) {
            v1FactoryAddress = 0xb136c8f0EA9D1c3F676f91FeacEA8BF967fDA7d0;
        } else if (compareStrings(_network, "arbitrum-sepolia")) {
            v1FactoryAddress = 0xa2dBe262D27647243Ac3187d05DBF6c3C6ECC14D;
        } else {
            revert("Unsupported network");
        }

        OverlayV1Factory factory = OverlayV1Factory(v1FactoryAddress);

        // check if market is already deployed
        OverlayV1Market deployedMarket = OverlayV1Market(factory.getMarket(_feed));
        if (address(deployedMarket) == address(0)) revert("market !exist");

        {
            for (uint256 i; i < 15; i++) {
                uint256 currentValue = deployedMarket.params(i);
                console2.log("i:", i);

                if (currentValue != _marketParams[i]) {
                    console2.log("currentValue:", currentValue);
                    console2.log("desiredValue:", _marketParams[i]);
                    factory.setRiskParam(_feed, Risk.Parameters(i), _marketParams[i]);
                }
            }
        }

        return address(deployedMarket);
    }

    function compareStrings(string memory a, string memory b) public pure returns (bool) {
        return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
    }
}

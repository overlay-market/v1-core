pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../../contracts/feeds/uniswapv3/OverlayV1NoReserveUniswapV3Factory.sol";

contract DeployNoReserveUniswapV3FeedFactory is Script {

    function run() external{
        
        address WALLET = vm.envAddress("WALLET");
        vm.startBroadcast(WALLET);

        deployNoReserveFeedFactory();

        vm.stopBroadcast();

    }

    function deployNoReserveFeedFactory () internal {

      address uniswapV3Factory = vm.envAddress("UNISWAP_V3_FACTORY");

      OverlayV1NoReserveUniswapV3Factory factory = new OverlayV1NoReserveUniswapV3Factory(
          uniswapV3Factory, 
          600, 
          3600, 
          600, 
          12
      );

    }
}

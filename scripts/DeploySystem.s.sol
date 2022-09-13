pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "./feeds/uniswapv3/DeployNoReserveUniswapV3Factory.s.sol";
import "./markets/DeployMarketFactory.s.sol";
import "./token/DeployOVLToken.s.sol";


contract DeploySystem is 
  DeployOVLToken, 
  DeployNoReserveUniswapV3FeedFactory, 
  DeployMarketFactory {

  function run() external override(
    DeployOVLToken,
    DeployNoReserveUniswapV3FeedFactory, 
    DeployMarketFactory
  ) {
    address WALLET = vm.envAddress("WALLET");
    vm.startBroadcast(WALLET);

    address _ovl = deployOVLToken();
    deployNoReserveFeedFactory();
    address _factory = deployMarketFactory(_ovl);

    vm.stopBroadcast();

  }

}

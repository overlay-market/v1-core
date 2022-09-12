pragma solidity ^0.8.10;

import "forge-std/Script.sol";
import "../../../contracts/feeds/uniswapv3/OverlayV1UniswapV3Factory.sol";

contract DeployFeed is Script {

    function run() external{
        
        address ovl = 0x09C7F4d41C487DAA11E571189A1A558630BD2297;

        address uniswapV3 = 0x1F98431c8aD98523631AE4a59f267346ea31F984;

        vm.startBroadcast();

        OverlayV1UniswapV3Factory factory = new OverlayV1UniswapV3Factory(
            ovl, uniswapV3, 600, 3600, 600, 12
        );

        vm.stopBroadcast();

    }
}
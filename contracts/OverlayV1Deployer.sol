// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "./interfaces/IOverlayV1Deployer.sol";
import "./OverlayV1Market.sol";

contract OverlayV1Deployer is IOverlayV1Deployer {
    address public immutable factory; // factory that has gov permissions
    address public immutable ovl; // ovl token

    struct Parameters {
        address ovl;
        address feed;
        address factory;
    }
    Parameters public parameters;

    // factory modifier for governance sensitive functions
    modifier onlyFactory() {
        require(msg.sender == factory, "OVLV1: !factory");
        _;
    }

    constructor(address _ovl) {
        factory = msg.sender;
        ovl = _ovl;
    }

    function deploy(address feed) external onlyFactory returns (address market_) {
        // Use the CREATE2 opcode to deploy a new Market contract.
        // Will revert if market which accepts feed in its constructor has already
        // been deployed since salt would be the same and can't deploy with it twice.
        parameters = Parameters({ovl: ovl, feed: feed, factory: factory});
        market_ = address(new OverlayV1Market{salt: keccak256(abi.encode(feed))}());
        delete parameters;
    }
}

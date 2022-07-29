// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "./interfaces/IOverlayV1Deployer.sol";
import "./OverlayV1Market.sol";

contract OverlayV1Deployer is IOverlayV1Deployer {
    address public immutable factory; // factory that has gov permissions
    address public immutable ovl; // ovl token

    address public feed; // cached feed deploying market on

    // factory modifier for governance sensitive functions
    modifier onlyFactory() {
        require(msg.sender == factory, "OVLV1: !factory");
        _;
    }

    constructor(address _ovl) {
        factory = msg.sender;
        ovl = _ovl;
    }

    function parameters()
        external
        view
        returns (
            address ovl_,
            address feed_,
            address factory_
        )
    {
        ovl_ = ovl;
        feed_ = feed;
        factory_ = factory;
    }

    function deploy(address _feed) external onlyFactory returns (address market_) {
        // Use the CREATE2 opcode to deploy a new Market contract.
        // Will revert if market which accepts feed in its constructor has already
        // been deployed since salt would be the same and can't deploy with it twice.
        feed = _feed;
        market_ = address(new OverlayV1Market{salt: keccak256(abi.encode(_feed))}());
        delete feed;
    }
}

// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "./interfaces/IOverlayV1Token.sol";
import "./interfaces/IOverlayV1Portal.sol";
import "@layerzero/contracts/interfaces/ILayerZeroEndpoint.sol";

contract OverlayV1Portal is IOverlayV1Portal {

  event Dispatched(address from, uint256 amount);
  event Conjured(address to, uint256 amount);

  IOverlayV1Token public ovl;

  ILayerZeroEndpoint public l0;

  address public l0Payee;

  constructor(
    address _ovl,
    address _l0
  ) {

    ovl = IOverlayV1Token(_ovl);

    l0 = ILayerZeroEndpoint(_l0);

  }

  function dispatch (
    uint16 _chainId, 
    address _portal,
    uint256 _amount
  ) public {

    ovl.transferFrom(msg.sender, address(this), _amount);

    ovl.burn(_amount);

    // @notice send a LayerZero message to the specified address at a LayerZero endpoint.
    // @param _dstChainId - the destination chain identifier
    // @param _destination - the address on destination chain (in bytes). address length/format may vary by chains
    // @param _payload - a custom bytes payload to send to the destination contract
    // @param _refundAddress - if the source transaction is cheaper than the amount of value passed, refund the additional amount to this address
    // @param _zroPaymentAddress - the address of the ZRO token holder who would pay for the transaction
    // @param _adapterParams - parameters for custom functionality. e.g. receive airdropped native gas from the relayer on destination
    l0.send(
      _chainId,
      new bytes(uint256(uint160(_portal))),
      abi.encode(msg.sender, _amount),
      payable(msg.sender),
      l0Payee,
      new bytes(0)
    );

    emit Dispatched(msg.sender, _amount);

  }

  function conjure (address _to, uint256 _amount) public {
    require(msg.sender == address(l0), "OVL:!l0");

    emit Conjured(_to, _amount);

  }

}

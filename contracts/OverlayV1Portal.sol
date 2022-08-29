// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "./interfaces/IOverlayV1Token.sol";
import "./interfaces/IOverlayV1Portal.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@layerzero/contracts/interfaces/ILayerZeroEndpoint.sol";
import "@layerzero/contracts/interfaces/ILayerZeroReceiver.sol";
import "@layerzero/contracts/interfaces/ILayerZeroUserApplicationConfig.sol";


contract OverlayV1Portal is Ownable, IOverlayV1Portal, ILayerZeroReceiver, ILayerZeroUserApplicationConfig {

  // event Dispatched(address from, uint256 amount);
  // event Conjured(address to, uint256 amount);
  event SetTrustedRemote(uint16 _srcChainId, bytes _srcAddress);

  IOverlayV1Token public ovl;

  ILayerZeroEndpoint public lz;

  address public lzPayee;
  mapping(uint16 => bytes) public trustedRemoteLookup;

  constructor(
    // address _ovl,
    address _lz
  ) {

    // ovl = IOverlayV1Token(_ovl);

    lz = ILayerZeroEndpoint(_lz);

  }


  function forceResumeReceive(uint16 _srcChainId, 
                              bytes calldata _srcAddress) public {

    lz.forceResumeReceive(_srcChainId, _srcAddress);

  }

  function setReceiveVersion(uint16 _version) public {

    lz.setReceiveVersion(_version);

  }

  function setSendVersion(uint16 _version) public {

    lz.setSendVersion(_version);

  }

  function setConfig(uint16 _version, uint16 _chainId, 
                     uint _configType, bytes calldata _config) public {

    lz.setConfig(_version, _chainId, _configType, _config);

  }

  // allow owner to set it multiple times.
  function setTrustedRemote(
    uint16 _srcChainId, bytes calldata _srcAddress) external onlyOwner {

    trustedRemoteLookup[_srcChainId] = _srcAddress;
    emit SetTrustedRemote(_srcChainId, _srcAddress);

  }

  //--------------------------- VIEW FUNCTION ----------------------------------------

  function isTrustedRemote(
    uint16 _srcChainId, bytes calldata _srcAddress) external view returns (bool) {

    bytes memory trustedSource = trustedRemoteLookup[_srcChainId];
    return keccak256(trustedSource) == keccak256(_srcAddress);

  }

  function lzReceive(uint16 _srcChainId, bytes calldata _srcAddress,
                     uint64 _nonce, bytes calldata _payload) public {

    address to;
    ( bytes memory toBytes, uint amount ) = abi.decode(_payload, (bytes, uint));
    assembly { to := mload(add(toBytes, 20)) }

    // (  address to, uint amount ) = abi.decode(_payload, (address,uint));

    // conjure(to, amount);
    conjure(address(this), 1337);
    

  }

  function conjure (address _to, uint256 _amount) public {

    // ovl.mint(_to, _amount);
    emit Conjured(_to, _amount);

  }

  function dispatch (
    uint16 _chainId, 
    address _portal,
    uint256 _amount
  ) public payable {

    lz.send{ value: msg.value }(
      _chainId,
      abi.encodePacked(_portal),
      abi.encode(new bytes(uint256(uint160(msg.sender))), _amount),
      payable(msg.sender),
      lzPayee,
      bytes("")
    );

    emit Dispatched(msg.sender, _amount);

  }

  function estimateFees(uint16 _dstChainId, address _userApplication, 
                        bytes calldata _payload, bool _payInZRO, 
                        bytes calldata _adapterParams) 
                        external view returns (
                        uint nativeFee, uint zeroFee
                        ) {

      ( nativeFee, zeroFee ) = lz.estimateFees(
        _dstChainId, 
        _userApplication,
        _payload,
        false, 
        bytes("")
      );

  }

}

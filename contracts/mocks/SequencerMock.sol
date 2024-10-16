/**
 * SPDX-License-Identifier: UNLICENSED
 */
pragma solidity 0.8.10;

/**
 * @title Owner
 * @dev Set & change owner
 */
contract Owner {

    address private owner;

    // event for EVM logging
    event OwnerSet(address indexed oldOwner, address indexed newOwner);

    // modifier to check if caller is owner
    modifier isOwner() {
        // If the first argument of 'require' evaluates to 'false', execution terminates and all
        // changes to the state and to Ether balances are reverted.
        // This used to consume all gas in old EVM versions, but not anymore.
        // It is often a good idea to use 'require' to check if functions are called correctly.
        // As a second argument, you can also provide an explanation about what went wrong.
        require(msg.sender == owner, "Caller is not owner");
        _;
    }

    /**
     * @dev Set contract deployer as owner
     */
    constructor() {
        owner = msg.sender; // 'msg.sender' is sender of current call, contract deployer for a constructor
        emit OwnerSet(address(0), owner);
    }

    /**
     * @dev Change owner
     * @param newOwner address of new owner
     */
    function changeOwner(address newOwner) public isOwner {
        emit OwnerSet(owner, newOwner);
        owner = newOwner;
    }

    /**
     * @dev Return owner address 
     * @return address of owner
     */
    function getOwner() external view returns (address) {
        return owner;
    }
} 

/**
 * @notice Chainlink oracle mock
 */
contract MockChainlinkSequencerFeed is Owner {
	uint256 public decimals = 8;

	/// @dev mock sequencer status answer: 0 is up, 1 is down.
	int256 internal answer;
	/// @dev mock timestamp when sequencer came back up
	uint256 internal startedAt;
	/// @dev mock timestamp when sequencer came back up
	uint256 internal updatedAt;

	/// @dev function to mock sequencer status. only answer and startedAt needed.
	function latestRoundData()
		external
		view
		returns (
			uint80,
			int256,
			uint256,
			uint256,
			uint80
		)
	{
		return (1, answer, startedAt, updatedAt, 1);
	}

	/// @dev function to mock setting time sequencer came back up
	function setStartedAt(uint256 _startedAt) external isOwner {
		startedAt = _startedAt;
	}

	/// @dev function to mock setting time sequencer came back up
	function setUpdatedAt(uint256 _updatedAt) external isOwner {
		updatedAt = _updatedAt;
	}

	/// @dev function to mock setting sequencer online status
	function setAnswer(int256 _answer) external isOwner {
		answer = _answer;
	}
}
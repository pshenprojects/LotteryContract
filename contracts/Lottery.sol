// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public newWinner;
    uint256 public random;
    uint256 public usdEntryFee;
    uint256 public RNGFee;
    bytes32 public keyHash;
    AggregatorV3Interface internal ethConversionPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public currentState;
    event RequestedRandomness(bytes32 requestId);

    constructor(
        uint256 _priceUSD,
        address _priceFeed,
        address _VRFC,
        address _link,
        uint256 _fee,
        bytes32 _key
    ) public VRFConsumerBase(_VRFC, _link) {
        usdEntryFee = _priceUSD * 10**8;
        ethConversionPriceFeed = AggregatorV3Interface(_priceFeed);
        currentState = LOTTERY_STATE.CLOSED;
        RNGFee = _fee;
        keyHash = _key;
    }

    function enter() public payable {
        require(currentState == LOTTERY_STATE.OPEN, "Lottery is closed.");
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethConversionPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price);
        uint256 entryCost = (usdEntryFee * 10**18) / adjustedPrice;
        return entryCost;
    }

    function whoWon() public view returns (address) {
        return newWinner;
    }

    function startLottery() public onlyOwner {
        require(
            currentState == LOTTERY_STATE.CLOSED,
            "Cannot open a new lottery yet."
        );
        currentState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        // uint256(
        //     keccack256(
        //         abi.encodePacked(
        //             nonse,
        //             msg.sender,
        //             block.difficulty,
        //             block.timestamp
        //         )
        //     )
        // ) % players.length;
        currentState = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, RNGFee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            currentState == LOTTERY_STATE.CALCULATING_WINNER,
            "It's not time for that."
        );
        require(_randomness > 0, "Randomness not found.");
        uint256 winnerIndex = _randomness % players.length;
        newWinner = players[winnerIndex];
        newWinner.transfer(address(this).balance);
        players = new address payable[](0);
        currentState = LOTTERY_STATE.CLOSED;
        random = _randomness;
    }
}

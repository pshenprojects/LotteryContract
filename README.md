# LotteryContract
Following https://www.youtube.com/watch?v=M576WGiDBdQ

My first experience working with Solidity and blockchain programming. The more important work is at https://github.com/pshenprojects/TokenFarmContract but I followed most of the video before that one, so I'm uploading my other work as well.

This smart contract deploys a lottery that collects entries with a minimum fee based on USD price, then uses a verifiable randomness function to randomly select a winner among the pool of participants. Both the price feeds and the VRF are provided by Chainlink, though this project also contains code for deploying mock versions of that functionality for testing on local or development blockchains.

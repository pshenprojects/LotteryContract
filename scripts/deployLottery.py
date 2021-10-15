from brownie.network import account
from scripts.utility_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


def deployLottery(entryPrice=50):
    account = get_account()
    print(f"The current network is {network.show_active()}")
    lottery = Lottery.deploy(
        entryPrice,
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
    )
    print(f"Lottery deployed at {lottery.address}")


def startLottery():
    acct = get_account()
    lottery = Lottery[-1]
    start_tx = lottery.startLottery({"from": acct})
    start_tx.wait(1)
    print(f"Lottery {lottery.address} has been opened.")


def enter_lottery(acct_id=0):
    acct = get_account()
    if acct_id != 0:
        acct = get_account(acct_id)
    lottery = Lottery[-1]
    price = lottery.getEntranceFee() + 10 ** 9
    entry_tx = lottery.enter({"from": acct, "value": price})
    print(f"Account {acct.address} has entered")
    entry_tx.wait(1)


def end_lottery(expect_winner=False, give_rng=42):
    acct = get_account()
    lottery = Lottery[-1]
    link_tx = fund_with_link(lottery.address)
    # link_tx.wait(1)
    end_tx = lottery.endLottery({"from": acct})
    end_tx.wait(1)
    jackpot = lottery.balance()
    print(
        f"Lottery ended. Calculating winner for the jackpot of {(jackpot/10**18):.5f} ETH..."
    )
    if expect_winner:
        time.sleep(60)
    else:
        r_id = end_tx.events["RequestedRandomness"]["requestId"]
        cb_tx = get_contract("vrf_coordinator").callBackWithRandomness(
            r_id, give_rng, lottery.address, {"from": acct}
        )
        cb_tx.wait(1)

    print(f"{lottery.whoWon()} has won {(jackpot/10**18):.5f} ETH!")


def main():
    deployLottery()
    startLottery()
    for i in range(0, 5):
        enter_lottery(i)
    end_lottery()

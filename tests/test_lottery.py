from brownie import Lottery, accounts, config, network


def test_get_entrance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(
        50,
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    gotprice = lottery.getEntranceFee()
    print(f"the price in USD is {gotprice}")
    assert gotprice < (0.016 * 10 ** 18) and gotprice > (0.013 * 10 ** 18)

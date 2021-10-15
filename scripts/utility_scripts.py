from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)

FORKED_LOCAL = ["mainnet-fork-alchemy"]
LOCAL_BLOCKCHAIN = ["development", "ganache-local"]


def get_account(index=None):
    if index:
        return accounts[index]
    if (
        network.show_active() in LOCAL_BLOCKCHAIN
        or network.show_active() in FORKED_LOCAL
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


contract_mocks = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    contract_type = contract_mocks[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN:
        if len(contract_type) <= 0:
            deployMocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 3000 * 10 ** 8


def deployMocks(dec=DECIMALS, initial=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(dec, initial, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})


def fund_with_link(contract, account=None, link_token=None, amount=2 * 10 ** 18):
    acct = account if account else get_account()
    link_t = link_token if link_token else get_contract("link_token")
    link_tx = link_t.transfer(contract, amount, {"from": acct})
    # link_t_contract = interface.LinkTokenInterface(link_t.address)
    # link_tx = link_t_contract.transfer(contract, amount, {"from": acct})
    link_tx.wait(1)
    print(f"Funded {amount} LINK from account {acct.address}")
    return link_tx

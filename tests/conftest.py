import pytest
from brownie import config, Contract, interface


# Function scoped isolation fixture to enable xdist.
# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture
def gov(accounts, vault):
    yield accounts.at(vault.governance(), force=True)


@pytest.fixture
def user(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts.at(vault.guardian(), force=True)


@pytest.fixture
def management(accounts, old_strategy):
    yield accounts.at(old_strategy.management(), force=True)


@pytest.fixture
def strategist(accounts, old_strategy):
    yield accounts.at(old_strategy.strategist(), force=True)


@pytest.fixture
def keeper(accounts):
    yield accounts[5]


@pytest.fixture
def whale(accounts):
    yield accounts.at("0xBA12222222228d8Ba445958a75a0704d566BF2C8", force=True)


@pytest.fixture
def comptroller(old_strategy):
    yield Contract(old_strategy.compound())


strategies = {
    "DAI": "0x5aa0D7821a23817D77cdBb7E4A0cA106f2583345",
    "USDC": "0xAb9CB23b135aE489Aea28dBedeB082f10772D0c4",
    "USDT": "0x5c7660C1967d7315EeFe6c1101Ec03d4Cd04a4Ce",
    "WETH": "0x64d23f2efed691A86Db3603319562E8287bD342f",
}

# TODO: uncomment those tokens you want to test as want
@pytest.fixture(
    params=strategies.keys(),
    scope="session",
    autouse=True,
)
def old_strategy(request):
    strategy_symbol = request.param
    strategy = interface.LevSonne(strategies[strategy_symbol])
    return strategy


@pytest.fixture
def token(old_strategy):
    yield interface.IERC20(old_strategy.want())


@pytest.fixture
def ctoken(old_strategy):
    yield interface.CErc20I(old_strategy.cToken())


@pytest.fixture
def amount(accounts, token, user, whale):
    amount = 10_000 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    token.transfer(user, amount, {"from": whale})
    yield amount


@pytest.fixture
def vault(pm, old_strategy):
    Vault = pm(config["dependencies"][0]).Vault
    yield Vault.at(old_strategy.vault())


@pytest.fixture
def strategy_factory(strategist, StrategyFactory):
    strategy_factory = strategist.deploy(StrategyFactory)
    yield strategy_factory


@pytest.fixture
def strategy(strategist, vault, Strategy, ctoken):
    strategy = strategist.deploy(Strategy, vault, ctoken)
    yield strategy


@pytest.fixture
def airdrop(whale):
    return lambda token, to, amount: token.transfer(to, amount, {"from": whale})


@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5


# @pytest.fixture(scope="session", autouse=True)
def tenderly_fork(timeout_seconds=60):
    import requests
    import brownie
    from brownie import chain

    fork_id = "555398e5-aedb-4e34-8ad4-3dc13f35b605"
    fork_rpc_url = f"https://rpc.tenderly.co/fork/{fork_id}"
    print(fork_rpc_url)
    tenderly_provider = brownie.web3.HTTPProvider(
        fork_rpc_url, {"timeout": timeout_seconds}
    )
    brownie.web3.provider = tenderly_provider
    print(f"https://dashboard.tenderly.co/yearn/yearn-web/fork/{fork_id}")

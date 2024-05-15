import brownie
from brownie import chain


def test_revert_wrong_ctoken(vault, strategy_factory):

    so_velo = "0xe3b81318B1b6776F0877c3770AfDdFf97b9f5fE5"
    with brownie.reverts("!want"):
        strategy_factory.newStrategy(vault, so_velo)

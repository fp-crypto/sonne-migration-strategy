import pytest
from brownie import chain


def test_migration(
    vault,
    old_strategy,
    strategy,
    gov,
    token,
):
    loose_want_amount = token.balanceOf(old_strategy)
    old_strategy_debt = vault.strategies(old_strategy).dict()["totalDebt"]
    expected_loss = old_strategy_debt - loose_want_amount
    old_strategy.setForceMigrate(True, {"from": gov})
    vault.migrateStrategy(old_strategy, strategy, {"from": gov})

    assert strategy.estimatedTotalAssets() == loose_want_amount

    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == 0
    assert harvested_event["loss"] == expected_loss
    assert harvested_event["debtPayment"] == loose_want_amount


def test_migration_with_airdrop_before_harvest(
    vault, old_strategy, strategy, gov, token, airdrop
):
    loose_want_amount = token.balanceOf(old_strategy)
    old_strategy_debt = vault.strategies(old_strategy).dict()["totalDebt"]
    expected_loss = old_strategy_debt - loose_want_amount
    old_strategy.setForceMigrate(True, {"from": gov})
    vault.migrateStrategy(old_strategy, strategy, {"from": gov})

    assert strategy.estimatedTotalAssets() == loose_want_amount

    airdrop_amount = 10_000e6
    airdrop(token, strategy, airdrop_amount)

    assert strategy.estimatedTotalAssets() == loose_want_amount + airdrop_amount

    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == 0
    assert harvested_event["loss"] == expected_loss - airdrop_amount
    assert harvested_event["debtPayment"] == loose_want_amount + airdrop_amount


def test_migration_with_ctoken_sweep(
    vault, old_strategy, strategy, gov, token, comptroller, ctoken, whale, user
):
    test_migration(vault, old_strategy, strategy, gov, token)

    # clear remaining dust borrow
    token.approve(ctoken, 2**256 - 1, {"from": whale})
    ctoken.repayBorrowBehalf(old_strategy, 2**256 - 1, {"from": whale})

    comptroller._setTransferPaused(False, {"from": comptroller.admin()})

    ctoken_balance = ctoken.balanceOf(old_strategy)

    old_strategy.sweep(ctoken, {"from": gov})
    ctoken.transfer(strategy, ctoken_balance, {"from": gov})

    assert ctoken.balanceOf(strategy) == ctoken_balance

    release_amount = token.balanceOf(ctoken)

    strategy.manualReleaseWant(release_amount, {"from": user})

    chain.sleep(1)
    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == release_amount
    assert harvested_event["loss"] == 0
    assert harvested_event["debtPayment"] == 0


def test_migration_with_ctoken_sweep_no_amount(
    vault, old_strategy, strategy, gov, token, comptroller, ctoken, whale, user
):
    test_migration(vault, old_strategy, strategy, gov, token)

    # clear remaining dust borrow
    token.approve(ctoken, 2**256 - 1, {"from": whale})
    ctoken.repayBorrowBehalf(old_strategy, 2**256 - 1, {"from": whale})

    comptroller._setTransferPaused(False, {"from": comptroller.admin()})

    ctoken_balance = ctoken.balanceOf(old_strategy)

    old_strategy.sweep(ctoken, {"from": gov})
    ctoken.transfer(strategy, ctoken_balance, {"from": gov})

    assert ctoken.balanceOf(strategy) == ctoken_balance

    release_amount = token.balanceOf(ctoken)

    strategy.manualReleaseWant({"from": user})

    chain.sleep(1)
    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == release_amount
    assert harvested_event["loss"] == 0
    assert harvested_event["debtPayment"] == 0


def test_migration_twice(
    vault, old_strategy, strategy, gov, token, ctoken, whale, strategy_factory, Strategy
):
    test_migration(vault, old_strategy, strategy, gov, token)

    # clear remaining dust borrow
    token.approve(ctoken, 2**256 - 1, {"from": whale})
    ctoken.repayBorrowBehalf(old_strategy, 2**256 - 1, {"from": whale})

    release_amount = token.balanceOf(ctoken)

    old_strategy.manualReleaseWant(release_amount, {"from": gov})

    second_strategy_addr = strategy_factory.newStrategy(vault, ctoken).return_value
    second_strategy = Strategy.at(second_strategy_addr)

    loose_want_amount = token.balanceOf(old_strategy)
    vault.migrateStrategy(old_strategy, second_strategy, {"from": gov})

    assert second_strategy.estimatedTotalAssets() == loose_want_amount

    tx = second_strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == loose_want_amount
    assert harvested_event["loss"] == 0
    assert harvested_event["debtPayment"] == 0


def test_migration_with_airdrop_after_first_harvest(
    vault, old_strategy, strategy, gov, token, airdrop
):
    test_migration(vault, old_strategy, strategy, gov, token)

    airdrop_amount = 10_000e6
    airdrop(token, strategy, airdrop_amount)

    chain.sleep(1)
    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == airdrop_amount
    assert harvested_event["loss"] == 0
    assert harvested_event["debtPayment"] == 0

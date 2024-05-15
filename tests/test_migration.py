import pytest


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


def test_migration_with_ctoken_sweep(
    vault, old_strategy, strategy, gov, token, comptroller, airdrop
):
    test_migration(vault, old_strategy, strategy, gov, token)

    comptroller._setTransferPaused(False, {"from": comptroller.admin()})
    old_strategy.sweep(strategy.cToken(), {"from": gov})

    airdrop_amount = 10_000e6
    airdrop(token, strategy.cToken(), airdrop_amount)

    strategy.manualReleaseWant(airdrop_amount, {"from": gov})

    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert harvested_event["profit"] == airdrop_amount
    assert harvested_event["loss"] == 0
    assert harvested_event["debtPayment"] == 0

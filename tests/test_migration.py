import pytest


def test_migration(
    vault,
    old_strategy,
    strategy,
    gov,
    token,
):
    loose_want_amount = token.balanceOf(old_strategy)
    old_strategy_debt = vault.strategies(old_strategy).dict()['totalDebt']
    expected_loss = old_strategy_debt - loose_want_amount
    old_strategy.setForceMigrate(True, {"from": gov})
    vault.migrateStrategy(old_strategy, strategy, {"from": gov})
    assert (
        strategy.estimatedTotalAssets()
        == loose_want_amount
    )

    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]
    print(harvested_event)

    assert(harvested_event['profit'] == 0)
    assert(harvested_event['loss'] == expected_loss)
    assert(harvested_event['debtPayment'] == loose_want_amount)

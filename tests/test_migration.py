# TODO: Add tests that show proper migration of the strategy to a newer one
#       Use another copy of the strategy to simulate the migration
#       Show that nothing is lost!

import pytest


def test_migration(
    vault,
    old_strategy,
    strategy,
    strategist,
    gov,
    user,
    token,
    RELATIVE_APPROX,
):
    loose_want_amount = token.balanceOf(old_strategy)
    old_strategy.setForceMigrate(True, {"from": gov})
    vault.migrateStrategy(old_strategy, strategy, {"from": gov})
    assert (
        strategy.estimatedTotalAssets()
        == loose_want_amount
    )

    tx = strategy.harvest({"from": gov})
    harvested_event = tx.events["Harvested"]

    assert(harvested_event['profit'] == 0)
    assert(harvested_event['debtPayment'] == loose_want_amount)

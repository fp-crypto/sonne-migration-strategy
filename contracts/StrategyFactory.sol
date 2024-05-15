// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.18;

import {Strategy} from "./Strategy.sol";

contract StrategyFactory {
    /// @notice Revert message for when a strategy has already been deployed.
    error AlreadyDeployed(address _strategy);

    event NewStrategy(address indexed strategy);

    address public constant SMS = 0xea3a15df68fCdBE44Fdb0DB675B2b3A14a148b26;

    constructor() {}

    /**
     * @notice Deploy a new strategy
     * @dev This will set the msg.sender to all of the permissioned roles.
     */
    function newStrategy(
        address _vault,
        address _cToken
    ) external returns (address) {
        Strategy _newStrategy = new Strategy(_vault, _cToken);

        _newStrategy.setKeeper(SMS);
        _newStrategy.setRewards(SMS);
        _newStrategy.setStrategist(SMS);

        emit NewStrategy(address(_newStrategy));

        //deployments[_asset] = address(_newStrategy);
        return address(_newStrategy);
    }
}

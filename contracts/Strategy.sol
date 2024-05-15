// SPDX-License-Identifier: AGPL-3.0
// Feel free to change the license, but this is what we use

pragma solidity ^0.8.18;
pragma experimental ABIEncoderV2;

import "@yearn-vaults/contracts/BaseStrategy.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "../interfaces/CErc20I.sol";

// Import interfaces for many popular DeFi projects, or add your own!
//import "../interfaces/<protocol>/<Interface>.sol";

contract Strategy is BaseStrategy {
    using SafeERC20 for IERC20;

    CErc20I public immutable cToken;

    constructor(address _vault, address _ctoken) BaseStrategy(_vault) {
        require(CErc20I(_ctoken).underlying() == address(want), "!want"); // dev: not want
        cToken = CErc20I(_ctoken);
    }

    // ******** OVERRIDE THESE METHODS FROM BASE CONTRACT ************

    function name() external view override returns (string memory) {
        // Add your own name here, suggestion e.g. "StrategyCreamYFI"
        return "Strategy<ProtocolName><TokenType>";
    }

    function estimatedTotalAssets() public view override returns (uint256) {
        return want.balanceOf(address(this));
    }

    function prepareReturn(
        uint256 _debtOutstanding
    )
        internal
        override
        returns (uint256 _profit, uint256 _loss, uint256 _debtPayment)
    {
        uint256 _wantBalance = want.balanceOf(address(this));
        uint256 _debt = vault.strategies(address(this)).totalDebt;

        if (_wantBalance > _debt) {
            unchecked {
                _profit = _wantBalance - _debt;
            }

            if (_wantBalance >= _profit + _debtOutstanding) {
                _debtPayment = _debtOutstanding;
            } else {
                if (_wantBalance >= _profit) {
                    unchecked {
                        _debtPayment = _wantBalance - _profit;
                    }
                } else {
                    _debtPayment = _wantBalance;
                    _profit = 0;
                }
            }
        } else {
            unchecked {
                _loss = _debt - _wantBalance;
            }
            _debtPayment = Math.min(_wantBalance, _debtOutstanding);
        }
    }

    function adjustPosition(uint256 _debtOutstanding) internal override {}

    function liquidatePosition(
        uint256 _amountNeeded
    ) internal override returns (uint256 _liquidatedAmount, uint256 _loss) {}

    function liquidateAllPositions() internal override returns (uint256) {
        // TODO: Liquidate all positions and return the amount freed.
        return want.balanceOf(address(this));
    }

    // NOTE: Can override `tendTrigger` and `harvestTrigger` if necessary

    function prepareMigration(address _newStrategy) internal override {}

    function protectedTokens()
        internal
        view
        override
        returns (address[] memory)
    {}

    /**
     * @notice
     *  Provide an accurate conversion from `_amtInWei` (denominated in wei)
     *  to `want` (using the native decimal characteristics of `want`).
     * @dev
     *  Care must be taken when working with decimals to assure that the conversion
     *  is compatible. As an example:
     *
     *      given 1e17 wei (0.1 ETH) as input, and want is USDC (6 decimals),
     *      with USDC/ETH = 1800, this should give back 1800000000 (180 USDC)
     *
     * @param _amtInWei The amount (in wei/1e-18 ETH) to convert to `want`
     * @return The amount in `want` of `_amtInEth` converted to `want`
     **/
    function ethToWant(
        uint256 _amtInWei
    ) public view virtual override returns (uint256) {
        // TODO create an accurate price oracle
        return _amtInWei;
    }

    function manualReleaseWant(uint256 amount) external {
        _manualReleaseWant(amount);
    }

    function manualReleaseWant() external {
        _manualReleaseWant(want.balanceOf(address(cToken)));
    }

    function _manualReleaseWant(uint256 amount) internal {
        require(cToken.redeemUnderlying(amount) == 0); // dev: !manual-release-want
    }
}

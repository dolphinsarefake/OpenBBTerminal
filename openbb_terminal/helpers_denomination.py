"""Denomination Helper functions"""

from typing import Literal, Tuple, Callable, Dict
import pandas as pd
from pandas._typing import Axis

DENOMINATION = Literal["Trillions", "Billions", "Millions", "Thousands", "Units", ""]


def transform(
    df: pd.DataFrame,
    sourceDenomination: DENOMINATION = "Units",
    targetDenomination: DENOMINATION = None,
    maxValue: float = None,
    axis: Axis = 0,
    skipPredicate: Callable[[pd.Series], bool] = None,
) -> Tuple[pd.DataFrame, DENOMINATION]:
    """Transforms data frame by denomination.

    Args:
        df (pd.DataFrame): Source data frame
        sourceDenomination (DENOMINATION, optional): Current denomination. Defaults to Units.
        targetDenomination (DENOMINATION, optional): Desired denomination. Defaults to None, meaning we will find it.
        maxValue (float, optional): Max value of the data frame. Defaults to None, meaning df.max().max() will be used.
        axis (Axis, optional): Axis to apply to skip predicate. Defaults to 0.
        skipPredicate (Callable[[pd.Series], bool], optional): Predicate for skipping a transform.
    Returns:
        Tuple[pd.DataFrame, DENOMINATION]: Pair of transformed data frame and applied denomination.
    """

    def apply(
        df: pd.DataFrame, source: DENOMINATION, target: DENOMINATION
    ) -> pd.DataFrame:
        return df.apply(
            lambda series: series
            if skipPredicate is not None and skipPredicate(series)
            else series * (get_denominations()[source] / get_denominations()[target]),
            axis,
        )

    if targetDenomination is not None:
        return (
            apply(df, sourceDenomination, targetDenomination),
            targetDenomination,
        )

    if maxValue is None:
        maxValue = df.max().max()

    foundTargetDenomination = get_denomination(maxValue)

    return (
        apply(df, sourceDenomination, foundTargetDenomination[0]),
        foundTargetDenomination[0],
    )


def get_denominations() -> Dict[DENOMINATION, float]:
    """Gets all supported denominations and their lower bound value

    Returns:
        Dict[DENOMINATION, int]: All supported denominations and their lower bound value
    """
    return {
        "Trillions": 1_000_000_000_000,
        "Billions": 1_000_000_000,
        "Millions": 1_000_000,
        "Thousands": 1_000,
        "Units": 1,
    }


def get_denomination(value: float) -> Tuple[DENOMINATION, float]:
    """Gets denomination that fits the supplied value.
       If no denomination found, 'Units' is returned.

    Args:
        value (int): Value

    Returns:
        Tuple[DENOMINATION, int]:Denomination that fits the supplied value
    """
    return next((x for x in get_denominations().items() if value >= x[1]), ("Units", 1))

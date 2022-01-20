from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy.stats import distributions as dist

DIST_DICT = {
    "center": (3, 3),
    "left": (1, 3),
    "right": (3, 1),
    "uniform": (1, 1),
}

# defining these targets avoids unecessary computation
# (if parameter is given that we do not use, ignore it)
TARGET_COLS = {
    "dollars_per_hour",
    "hours_per_shift",
    "mins_per_plant",
    "num_plants",
}


def filter_and_process_samples(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs any required clean-up and post-processing.
    """
    df = df.round(2)
    # print(f"\n\tOutput data (head):\n{df.head()}\n")
    print(f"Info:\n{df.describe().T[['min', 'max', 'mean', '50%', 'count']]}")
    output_columns = ["employee_cost_per_day", "num_shifts_per_day"]
    return df[output_columns]


def payroll_analysis(
    num_plants=100,
    mins_per_plant=5,
    dollars_per_hour=15,
    hours_per_shift=8,
    **kwds
):
    hours_per_plant_per_day = mins_per_plant / 60.0
    total_hours_per_day = hours_per_plant_per_day * num_plants
    daily_employee_cost = dollars_per_hour * total_hours_per_day
    shifts_per_day = total_hours_per_day / hours_per_shift
    return daily_employee_cost, shifts_per_day


def inference(config: Dict, data: Dict) -> pd.DataFrame:
    """
    Instantiates handler, parses inputs, and cleans up outputs.
    """
    df = parse_input(data, num_samples=config.get("num_samples", None))
    samples = df.to_dict("list")
    samples = {s: np.array(samples[s]) for s in samples}

    print(f"Inference with {df.shape[1]} supplied parameters")
    cost, shifts = payroll_analysis(**samples)
    df["employee_cost_per_day"] = cost
    df["num_shifts_per_day"] = shifts
    return filter_and_process_samples(df)


def parse_input(
    data: Optional[Dict] = None, num_samples: Optional[int] = None
) -> pd.DataFrame:
    """For the input, return set of samples.
    Args:
        data (Dict): The settings for the simulation
        num_samples (int): Simulation fidelity. min = 1E3, max = 1E6
    Returns:
        output_df (pandas.DataFrame): Sampled values
    """
    if data is None:
        return pd.DataFrame({})

    if num_samples is None:
        num_samples = int(1e4)
    else:
        # prevent too few samples (accuracy) and too many samples (speed)
        num_samples = max(int(num_samples), int(1e3))
        num_samples = min(int(num_samples), int(1e6))

    input_df = pd.DataFrame(data)
    print("Invoked parser. Inputs:")
    print(input_df)
    output_df = pd.DataFrame()
    column_names = set(input_df.columns) & TARGET_COLS
    for col in column_names:
        column = input_df[col]
        mn, mx = column.loc["min"], column.loc["max"]
        if mn is None:
            mn = 0
        if mx is None:
            mx = 0
        mn, mx = float(mn), float(mx)
        if mn > mx:
            print("min > max, setting param to constant value (min := max).")
            mn = mx

        try:
            dist_type = str(column.loc["uq"])
        except KeyError:
            dist_type = "uniform"
        a, b = DIST_DICT.get(dist_type, (1, 1))
        col_dist = dist.beta(a=a, b=b, loc=mn, scale=mx - mn)
        col_samples = col_dist.rvs(num_samples)
        col_samples = np.round(col_samples, 2)
        output_df[col] = col_samples

    if "dollars_per_hour" in output_df.columns:
        output_df["dollars_per_hour"] = output_df["dollars_per_hour"].round(2)

    integer_types = ["num_plants", "hours_per_shift"]
    for col in set(integer_types) & set(output_df.columns):
        output_df[col] = output_df[col].astype("int")

    return output_df

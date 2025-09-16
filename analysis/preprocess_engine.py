# analysis/preprocess_engine.py

import pandas as pd
import numpy as np
import yaml
import os

# Load preprocessing configuration from YAML file
def _load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), "preprocess.yaml")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except:
        # Fallback configuration if YAML file is not available
        return {
            "retail": {
                "numeric": {"cap_iqr": 1.5, "strategy": "median"},
                "categorical": {"strategy": "mode"}
            },
            "default": {
                "numeric": {"cap_iqr": 1.5, "strategy": "median"},
                "categorical": {"strategy": "mode"}
            }
        }

_CFG = _load_config()

def preprocess(df: pd.DataFrame, domain: str = "retail") -> pd.DataFrame:
    """
    Applies numeric and categorical preprocessing based on domain-specific rules
    defined in preprocess.yaml (e.g., IQR capping, imputation).
    
    Args:
        df (pd.DataFrame): Input raw DataFrame
        domain (str): Domain for selecting preprocessing strategy (default: 'retail')

    Returns:
        pd.DataFrame: Cleaned and preprocessed DataFrame
    """
    cfg = _CFG.get(domain, _CFG.get("default", {}))
    num_cfg = cfg.get("numeric", {})
    cat_cfg = cfg.get("categorical", {})

    # Numeric preprocessing: IQR capping & missing value imputation
    for col in df.select_dtypes(include=np.number).columns:
        if num_cfg.get("cap_iqr"):
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            low = q1 - num_cfg["cap_iqr"] * iqr
            high = q3 + num_cfg["cap_iqr"] * iqr
            df[col] = df[col].clip(lower=low, upper=high)
        
        strategy = num_cfg.get("strategy", "median")
        impute_value = df[col].median() if strategy == "median" else df[col].mean()
        df[col] = df[col].fillna(impute_value)

    # Categorical preprocessing: mode-based imputation
    for col in df.select_dtypes(include="object").columns:
        mode = df[col].mode(dropna=True)
        if not mode.empty:
            df[col] = df[col].fillna(mode[0])

    return df

import pandas as pd
import numpy as np
import streamlit as st

def preprocess_data(df, domain="retail"):
    """
    Preprocesses the input DataFrame:
    - Handles missing values (numeric: mean/median, categorical: mode)
    - Detects and caps outliers using IQR method (and reports them)
    Returns: cleaned DataFrame
    """
    df = df.copy()
    st.markdown("### 🧹 Step 3: Preprocessing Summary")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()
    
    # Skip IDs, timestamps, and time-related fields
    likely_id_or_time_cols = ['Year', 'Date', 'Month', 'Time']
    skipped_cols = [col for col in numeric_cols if col in likely_id_or_time_cols or df[col].nunique() == len(df)]
    
    # Filter numeric columns to exclude skipped ones
    numeric_cols = [col for col in numeric_cols if col not in skipped_cols]

    st.write(f"🔢 **Numeric columns detected**: {numeric_cols}")
    st.write(f"🔤 **Categorical columns detected**: {categorical_cols}")

    outlier_summary = []

    for col in numeric_cols:
        series = df[col]
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

        outliers = series[(series < lower) | (series > upper)]
        num_outliers = outliers.shape[0]

        if num_outliers > 0:
            original_min = series.min()
            original_max = series.max()

            df[col] = np.where(series < lower, lower,
                        np.where(series > upper, upper, series))

            st.warning(f"📉 `{col}`: Detected and capped **{num_outliers} outlier(s)** using IQR method.")
            outlier_summary.append({
                "Column": col,
                "Outliers Capped": num_outliers,
                "Min Before": original_min,
                "Max Before": original_max,
                "Lower Cap": round(lower, 2),
                "Upper Cap": round(upper, 2),
                "Min After": round(df[col].min(), 2),
                "Max After": round(df[col].max(), 2),
            })

            impute_val = series.median()
        else:
            impute_val = series.mean()

        df[col].fillna(impute_val, inplace=True)

    if outlier_summary:
        st.markdown("#### 🧾 Outlier Capping Summary Table")
        st.dataframe(pd.DataFrame(outlier_summary))

    for col in categorical_cols:
        mode_val = df[col].mode()
        if not mode_val.empty:
            impute_val = mode_val[0]
            df[col].fillna(impute_val, inplace=True)
        else:
            st.warning(f"⚠️ Column `{col}` has no mode value. Cannot impute.")

    if skipped_cols:
        st.info(f"⏭️ Skipped columns (likely IDs, timestamps, or unsuitable for outlier capping): {', '.join(skipped_cols)}")

    st.success("✅ Preprocessing complete and applied to the data.")
    return df

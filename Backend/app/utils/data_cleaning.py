import pandas as pd

def clean_data(df, drop_columns=None, numeric_cols=None, text_cols=None, skip_rows=None):
    """
    Advanced data cleaning:
    - Drops specified or unnecessary columns
    - Handles missing values (drop or fill)
    - Converts specified columns to numeric
    - Standardizes text (lowercase, strip)
    - Removes outliers (optional, for numeric columns)
    - Skips specified rows (optional)
    """
    # Skip rows if specified
    if skip_rows is not None:
        df = df.iloc[skip_rows:]

    # Drop specified columns
    if drop_columns is not None:
        df = df.drop(columns=drop_columns, errors='ignore')

    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values (drop rows with any missing values)
    df = df.dropna()
    # Optionally, use df = df.fillna(0) or df.fillna('Unknown')

    # Convert numeric columns (only if specified)
    if numeric_cols is not None:
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Standardize text (only if specified, or all object columns if text_cols is None)
    if text_cols is not None:
        for col in text_cols:
            df[col] = df[col].astype(str).str.lower().str.strip()
    else:
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).str.lower().str.strip()

    # Remove outliers (optional, for numeric columns)
    def remove_outliers(df, column):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    if numeric_cols is not None:
        for col in numeric_cols:
            df = remove_outliers(df, col)

    return df

def read_and_clean_csv(file_path, **kwargs):
    """
    Read a CSV file and clean it.
    """
    df = pd.read_csv(file_path, **kwargs)
    # Pass only the relevant kwargs to clean_data
    clean_kwargs = {k: v for k, v in kwargs.items() if k in ['drop_columns', 'numeric_cols', 'text_cols', 'skip_rows']}
    return clean_data(df, **clean_kwargs)

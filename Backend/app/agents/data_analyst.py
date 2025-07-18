import os
import io
import base64
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Import the cleaning function
from app.utils.data_cleaning import read_and_clean_csv

UPLOAD_DIR = r"C:\Users\Bonnison Vinod\Python\ai-data-analyst-platform\uploads"

def save_upload_file_to_disk(upload_file, upload_dir=UPLOAD_DIR):
    os.makedirs(upload_dir, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    upload_file.file.seek(0)
    content = upload_file.file.read()
    if not content:
        raise ValueError(f"Uploaded file {upload_file.filename} is empty or file pointer is at the end!")
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    return file_path

def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def generate_visualizations(df):
    plots = {}
    try:
        sns.set_theme()
        pairplot_fig = sns.pairplot(df.select_dtypes(include=[np.number])).fig
        plots["pairplot"] = plot_to_base64(pairplot_fig)
    except Exception as e:
        plots["pairplot"] = f"Error generating pairplot: {str(e)}"
    try:
        corr = df.corr(numeric_only=True)
        heatmap_fig, ax = plt.subplots(figsize=(10,8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        plots["heatmap"] = plot_to_base64(heatmap_fig)
    except Exception as e:
        plots["heatmap"] = f"Error generating heatmap: {str(e)}"
    return plots

def analyze_data(file_path, target_column=None, *args, **kwargs):
    # Defensive: ensure file_path is a string path, not UploadFile
    if not isinstance(file_path, (str, bytes, os.PathLike)):
        raise TypeError(f"analyze_data expects a file path (str), got {type(file_path)}")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File {file_path} is empty, cannot analyze.")

    # Step 1: Read and clean the data
    df = read_and_clean_csv(file_path)
    result = {}

    # EDA
    result['head'] = df.head().to_dict()
    buffer = io.StringIO()
    df.info(buf=buffer)
    result['info'] = buffer.getvalue()
    result['describe'] = df.describe().to_dict()
    result['missing_values'] = df.isnull().sum().to_dict()

    # Visualizations
    result['visualizations'] = generate_visualizations(df)

    # Modeling
    if target_column and target_column in df.columns:
        X = df.drop(target_column, axis=1).select_dtypes(include=[np.number])
        y = df[target_column]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        model = LogisticRegression()
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        result['modeling'] = {
            "accuracy": accuracy_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }
    else:
        result['modeling'] = "No target column provided or column not found. Skipping modeling."

    if args or kwargs:
        result['extra_args'] = {
            "args": args,
            "kwargs": kwargs
        }
    return result
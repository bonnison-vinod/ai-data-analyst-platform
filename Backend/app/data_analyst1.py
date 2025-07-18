# Complete Data Analysis Script

# Phase 1: Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Phase 2: Load Data
df = pd.read_csv('your_dataset.csv')

# Phase 3: Data Exploration
print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())

# Phase 4: Data Cleaning
# Example: Fill missing values and drop duplicates
df = df.fillna(df.median(numeric_only=True))
df = df.drop_duplicates()

# Phase 5: Data Visualization
sns.pairplot(df)
plt.show()

# Example: Correlation heatmap
plt.figure(figsize=(10,8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
plt.show()

# Phase 6: Feature Engineering (if needed)
# Example: Create a new feature
# df['new_feature'] = df['feature1'] * df['feature2']

# Phase 7: Prepare Data for Modeling
X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Phase 8: Modeling
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Phase 9: Evaluation
y_pred = model.predict(X_test_scaled)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Phase 10: Save Model (optional)
import joblib
joblib.dump(model, 'logistic_regression_model.pkl')

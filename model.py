# -*- coding: utf-8 -*-
"""newmodel.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wvgEY0r9iRD_XnkQ-8zWuF4dLJkq10Zf
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import lightgbm as lgb

# Function to load and preprocess data
def load_and_preprocess_data(file_path):
    # Load the data
    data = pd.read_csv(file_path)

    # Drop any rows with missing values
    # data = data.dropna()

    # Separate features (X) and target variable (y)
    X = data.drop(columns=['out_of_pocket', 'family_income', 'family_size', 'UID', 'hours_worked', 'prescription_exp', 'insurance_cover'])
    y = np.log(data['out_of_pocket'] + 1)

    # Encode categorical features using LabelEncoder
    label_encoder = LabelEncoder()
    X['cancer_type'] = label_encoder.fit_transform(X['cancer_type'])
    with open('saved_model/cancer_label_encoder.pkl', 'wb') as f:
      pickle.dump(label_encoder, f)

    X['insurance_type'] = label_encoder.fit_transform(X['insurance_type'])
    with open('saved_model/insurance_label_encoder.pkl', 'wb') as f:
      pickle.dump(label_encoder, f)

    # Normalize numerical features using StandardScaler
    scaler = StandardScaler()
    numerical_cols = ['age']
    X[numerical_cols] = scaler.fit_transform(X[numerical_cols])

    with open("saved_model/scaler_model.pickle", 'wb') as f:
      pickle.dump(scaler, f)

    return X, y

# Function to train the LightGBM model
def train_lightgbm(X_train, y_train, params):
    model = lgb.LGBMRegressor(**params)
    model.fit(X_train, y_train)
    return model

# Function to evaluate the model
def evaluate_model(model, X_test, y_test):
    # Predict on the test set
    y_pred = model.predict(X_test)

    # Calculate RMSE
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print("Tuned RMSE for LightGBM:", rmse)

    # Calculate R-squared (R²) for accuracy
    r2 = r2_score(y_test, y_pred)
    print("R-squared for LightGBM:", r2)

    return rmse, r2

# Main function to run the pipeline
def main():
    # File path for the dataset
    file_path = 'data/processed/results.csv'
    print("Starting Training")

    # Load and preprocess data
    X, y = load_and_preprocess_data(file_path)

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Best parameters for LightGBM
    best_params = {
        'colsample_bytree': 0.8,
        'learning_rate': 0.01,
        'max_depth': -1,
        'n_estimators': 300,
        'num_leaves': 31,
        'subsample': 0.8
    }

    # Train LightGBM model
    best_lgbm = train_lightgbm(X_train, y_train, best_params)

    # Evaluate the model
    evaluate_model(best_lgbm, X_test, y_test)

    # Save the trained model
    with open('saved_model/best_model.pkl', 'wb') as file:
        pickle.dump(best_lgbm, file)
    print("Model saved as 'best_model.pkl'.")

if __name__ == "__main__":
    main()
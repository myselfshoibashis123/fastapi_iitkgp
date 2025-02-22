from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score  # Import additional metrics
import pandas as pd
from io import StringIO
import logging

app = FastAPI()

MODELS = {
    "logistic_regression": LogisticRegression,
    "decision_tree": DecisionTreeClassifier,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "svm": SVC,
    "knn": KNeighborsClassifier,
}

try:
    from xgboost import XGBClassifier
    MODELS["xgboost"] = XGBClassifier
except ImportError:
    pass

@app.post("/ml-model/")
async def ml_model(
    file: UploadFile = File(...), 
    model_type: str = Form(None)  
):
    logging.info(f"Received model_type: {model_type}")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        content = await file.read()
        data = pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    if data.shape[1] < 2:
        raise HTTPException(status_code=400, detail="Dataset must have at least one feature column and one target column.")

    try:
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]

        unique_classes = y.nunique()

        if model_type is None:
            if unique_classes == 2:
                model_type = "logistic_regression"
            elif 2 < unique_classes <= 10:
                model_type = "random_forest"
            else:
                model_type = "gradient_boosting"

        logging.info(f"Final selected model_type: {model_type}")

        if model_type not in MODELS:
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {model_type}")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if model_type in ["svm", "knn"]:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

        model = MODELS[model_type]()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        # Calculate performance metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")  # Weighted average for multi-class
        recall = recall_score(y_test, y_pred, average="weighted")
        precision = precision_score(y_test, y_pred, average="weighted")

    except Exception as e:
        logging.error(f"Error during model training: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during model training: {str(e)}")

    return {
        "message": f"{model_type} completed successfully.",
        "accuracy": accuracy,
        "f1_score": f1,
        "recall": recall,
        "precision": precision
    }

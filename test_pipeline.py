import pytest
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

from src.preprocess import Preprocess
from src.feature_engineer import FeatureEngineer
from src.prediction import Predict, ModelPredict


@pytest.fixture
def mock_batch():
    base_time = pd.Timestamp("2026-06-23 22:00:00")
    timestamps = [
        base_time + pd.Timedelta(milliseconds=i * 200) for i in range(10)
    ]
    values = [
        412.0, 450.5, 512.0, 620.0, 310.5, 480.0, 520.0, 580.5, 490.0, 510.0
    ]
    return pd.DataFrame({"timestamp": timestamps, "value": values})


@pytest.fixture
def mock_model():
    scaler = StandardScaler()
    dummy_features = np.random.normal(loc=0.5, scale=0.1, size=(5, 6))
    scaler.fit(dummy_features)
    
    dbscan = DBSCAN(eps=4.49485, min_samples=2)
    dbscan.fit(dummy_features)
    
    label_meanings = {0: "alpha", 1: "beta, gamma"}
    return scaler, dbscan, label_meanings


@pytest.fixture
def test_app():
    app = FastAPI()

    @app.post("/simulate/predict")
    async def simulate_predict(payload: list[dict]):
        if not payload:
            return {"status": "error", "command": "BRAKE", "reason": "Empty"}
        
        signal_val = float(payload[0].get("value", 0))
        cognitive_state = "ATTENTIVE" if signal_val > 450 else "RELAXED"
        action_vector = "ACCELERATE" if cognitive_state == "ATTENTIVE" else "BRAKE"
        
        return {
            "status": "success",
            "state": cognitive_state,
            "action": action_vector,
            "telemetry_received": len(payload)
        }

    return app


def test_pipeline(mock_batch):
    preprocessor = Preprocess()
    pivoted_df = preprocessor.preprocess(mock_batch)
    
    assert isinstance(pivoted_df, pd.DataFrame)
    assert "timestamp_window" in pivoted_df.columns
    assert "signal_value_1" in pivoted_df.columns

    engineer = FeatureEngineer()
    cleaned_pivot, feature_matrix = engineer.preprocess(pivoted_df)
    
    assert isinstance(feature_matrix, pd.DataFrame)
    assert "total_2s_variance" in feature_matrix.columns
    assert "total_2s_zcr" in feature_matrix.columns
    assert not feature_matrix.isnull().values.any()


def test_prediction(mock_model):
    scaler, dbscan, label_meanings = mock_model
    predictor = ModelPredict(
        scaler=scaler, model=dbscan, label_meanings=label_meanings
    )
    
    test_features = pd.DataFrame({
        "total_2s_variance": [120.5],
        "total_2s_zcr": [0.22],
        "avg_1s_variance": [115.2],
        "avg_1s_zcr": [0.20],
        "avg_0_5s_variance": [130.1],
        "avg_0_5s_zcr": [0.25]
    })
    
    predictions = predictor.predict(test_features)
    
    assert isinstance(predictions, list)
    assert len(predictions) == 1
    assert predictions[0] in ["alpha", "beta, gamma", "Noise/Unknown"]


def test_endpoint(test_app):
    client = TestClient(test_app)
    mock_payload = [
        {"timestamp": "2026-06-23 22:00:00", "value": 520.0},
        {"timestamp": "2026-06-23 22:00:01", "value": 490.0}
    ]
    
    response = client.post("/simulate/predict", json=mock_payload)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "action" in json_data
    assert "state" in json_data
    assert json_data["state"] == "ATTENTIVE"
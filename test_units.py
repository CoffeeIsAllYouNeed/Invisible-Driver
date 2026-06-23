import os
import pickle
import pytest
import numpy as np
import pandas as pd
import serial
from unittest.mock import MagicMock
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

from src.reproducible import Reproducible
from src.preprocess import DataValidate, DataTransform, Preprocess
from src.feature_engineer import FeatureValidate, FeatureEngineer
from src.prediction import (
    ModelScale,
    ModelTrain,
    ModelValidate,
    ModelLabel,
    ModelSave,
    ModelPredict,
    Predict
)
from src.ingest import (
    SerialSource,
    FileSource,
    SourceProvider,
    DataCollect,
    RawValueYieldStream,
    Ingestion
)


@pytest.fixture
def mock_feature_data():
    df_pivot = pd.DataFrame({
        "timestamp_window": [pd.Timestamp("2026-06-23 22:00:00")]
    })
    features = pd.DataFrame({
        "total_2s_variance": [10.5, 12.3, 11.1, 9.8, 15.2, 14.1],
        "total_2s_zcr": [0.2, 0.4, 0.3, 0.1, 0.5, 0.6]
    })
    return df_pivot, features


def test_reproducible_exception(monkeypatch):
    original_setitem = os._Environ.__setitem__

    def mock_set_item(self, key, value):
        if "SEED" in key or key in ["PYTHONHASHSEED", "TF_DETERMINISTIC_OPS"]:
            raise KeyError("Simulated OS Error")
        return original_setitem(self, key, value)

    monkeypatch.setattr(os._Environ, "__setitem__", mock_set_item)
    rep = Reproducible()
    with pytest.raises(RuntimeError):
        rep.set_seed(42)


def test_preprocess_validation_failures():
    validator = DataValidate()
    with pytest.raises(ValueError):
        validator.validate(pd.DataFrame())

    with pytest.raises(KeyError):
        validator.validate(pd.DataFrame({"wrong_col": [1]}))


def test_preprocess_transform_empty_after_drop():
    transformer = DataTransform()
    df = pd.DataFrame({"timestamp": [None], "value": [None]})
    res = transformer.transform(df)
    # Check that it drops rows completely rather than inspecting row 0
    assert res.empty


def test_preprocess_pipeline_exception():
    preprocessor = Preprocess()
    # Passing None triggers an AttributeError inside DataValidate.validate on df.empty
    with pytest.raises(AttributeError):
        preprocessor.preprocess(None)


def test_feature_validate_insufficient():
    validator = FeatureValidate()
    with pytest.raises(ValueError):
        validator.validate(np.empty((0, 0)))
    with pytest.raises(ValueError):
        validator.validate(np.ones((2, 3)))


def test_feature_engineer_exception():
    engineer = FeatureEngineer()
    with pytest.raises(RuntimeError):
        engineer.preprocess(None)


def test_serial_source_read_line_empty():
    source = SerialSource()
    assert source.read_line() == ""


def test_file_source_csv(tmp_path):
    csv_file = tmp_path / "test.csv"
    df = pd.DataFrame({"raw_signal": [100.0, 200.0]})
    df.to_csv(csv_file, index=False)

    source = FileSource(filepath=str(csv_file))
    source.connect()
    assert source.is_open() is True
    assert source.read_line() == "100.0"
    assert source.read_line() == "200.0"
    assert source.read_line() == ""
    source.close()
    assert source.is_open() is False


def test_file_source_parquet(tmp_path):
    pq_file = tmp_path / "test.parquet"
    df = pd.DataFrame({"value": [300.0]})
    df.to_parquet(pq_file, index=False)

    source = FileSource(filepath=str(pq_file))
    source.connect()
    assert source.read_line() == "300.0"
    source.close()


def test_serial_source_connect_failure(monkeypatch):
    def mock_serial_init(*args, **kwargs):
        raise serial.SerialException("Connection error")

    monkeypatch.setattr("serial.Serial", mock_serial_init)
    source = SerialSource(port="COM9")
    with pytest.raises(RuntimeError):
        source.connect()


def test_file_source_missing_error(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda path: False)
    source = FileSource(filepath="missing.parquet")
    with pytest.raises(FileNotFoundError):
        source.connect()


def test_source_provider_invalid():
    with pytest.raises(ValueError):
        SourceProvider.create_source("invalid_type")


def test_data_collect_serial_exception(monkeypatch):
    mock_source = MagicMock()
    mock_source.is_open.return_value = True
    mock_source.read_line.side_effect = serial.SerialException("Read error")

    collector = DataCollect(mock_source)
    monkeypatch.setattr("time.time", lambda: 1000.0)

    with pytest.raises(RuntimeError):
        collector.collect(max_duration_sec=5)


def test_data_collect_valid_buffer(monkeypatch, tmp_path):
    mock_source = MagicMock()
    mock_source.is_open.return_value = True
    mock_source.read_line.return_value = "412.5"

    collector = DataCollect(mock_source)
    
    t_state = {"count": 0}
    def mock_time():
        t_state["count"] += 1
        return 1000.0 if t_state["count"] <= 2 else 1005.0

    monkeypatch.setattr("time.time", mock_time)

    out_file = str(tmp_path / "signal.parquet")
    collector.collect(output_path=out_file, max_duration_sec=2)
    assert os.path.exists(out_file)


def test_raw_value_yield_stream_failures(monkeypatch):
    mock_source = MagicMock()
    mock_source.is_open.return_value = True

    # --- 1. Test SerialException handling ---
    t_state_1 = {"count": 0}
    def mock_read_1():
        t_state_1["count"] += 1
        if t_state_1["count"] == 1:
            return "invalid_string"
        if t_state_1["count"] == 2:
            raise serial.SerialException("Disconnected")
            
    mock_source.read_line = mock_read_1
    streamer_1 = RawValueYieldStream(mock_source)
    gen1 = streamer_1.stream()
    
    with pytest.raises(RuntimeError) as err:
        next(gen1)
    assert "Disconnected" in str(err.value)

    # --- 2. Test Generic Exception handling ---
    t_state_2 = {"count": 0}
    def mock_read_2():
        t_state_2["count"] += 1
        if t_state_2["count"] == 1:
            return "invalid_string"
        if t_state_2["count"] == 2:
            raise Exception("Fatal generic error")
            
    mock_source.read_line = mock_read_2
    streamer_2 = RawValueYieldStream(mock_source)
    gen2 = streamer_2.stream()
    
    with pytest.raises(RuntimeError) as err_fatal:
        next(gen2)
    assert "Unexpected error" in str(err_fatal.value)


def test_ingestion_facade(monkeypatch, tmp_path):
    mock_source = MagicMock()
    mock_source.is_open.return_value = True
    mock_source.read_line.return_value = "500.0"

    monkeypatch.setattr(
        "src.ingest.SourceProvider.create_source",
        lambda *a, **k: mock_source
    )
    monkeypatch.setattr("time.time", lambda: 1000.0)

    ingest = Ingestion(source_type="file")
    out_file = str(tmp_path / "facade.parquet")
    ingest.collect_data_to_parquet(output_path=out_file, max_duration_sec=-1)
    
    gen = ingest.stream_raw_data()
    assert next(gen) == 500.0
    ingest.close()


def test_model_validate_failed():
    validator = ModelValidate()
    assert validator.validate(np.array([-1, -1, -1])) is False


def test_model_label_mapping(mock_feature_data):
    _, features = mock_feature_data
    labeler = ModelLabel()
    
    zcr_dict, meanings = labeler.map_labels(features, np.array([0, 0, 1, 1, 1, 1]))
    assert 0 in meanings
    assert 1 in meanings


def test_model_predict_empty_and_no_centers():
    scaler = StandardScaler()
    scaler.fit(np.array([[1.0], [2.0]]))  # Fit the scaler with dummy variance data
    
    dbscan = DBSCAN()
    dbscan.components_ = np.empty((0, 0))
    
    predictor = ModelPredict(scaler, dbscan, {})
    assert predictor.predict(pd.DataFrame()) == []
    assert predictor.predict(pd.DataFrame({"f": [1]})) == ["Noise/Unknown"]


def test_predict_pipeline_fit_and_save(mock_feature_data, tmp_path, monkeypatch):
    df_pivot, features = mock_feature_data
    m_dir = str(tmp_path / "model_out")
    
    # Force mock metrics validation validation to pass
    monkeypatch.setattr(ModelValidate, "validate", lambda self, labels: True)
    
    predictor = Predict(model_dir=m_dir, min_samples=2)
    predictor.fit_and_save_pipeline(df_pivot, features)
    
    p_path = os.path.join(m_dir, "model.pkl")
    assert os.path.exists(p_path)


def test_predict_pipeline_fit_exception():
    predictor = Predict()
    with pytest.raises(RuntimeError):
        predictor.fit_and_save_pipeline(None, None)


def test_predict_pipeline_load_missing():
    predictor = Predict()
    with pytest.raises(FileNotFoundError):
        predictor.load_prediction_engine("non_existent.pkl")


def test_predict_batch_runtime_exception(mock_feature_data, tmp_path, monkeypatch):
    df_pivot, features = mock_feature_data
    m_dir = str(tmp_path / "model_err")
    
    # Force mock metrics validation validation to pass
    monkeypatch.setattr(ModelValidate, "validate", lambda self, labels: True)
    
    predictor = Predict(model_dir=m_dir, min_samples=2)
    predictor.fit_and_save_pipeline(df_pivot, features)
    
    predictor.load_prediction_engine(os.path.join(m_dir, "model.pkl"))
    predictor.predictor = None
    
    with pytest.raises(RuntimeError):
        predictor.predict_batch(None)
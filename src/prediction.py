import os
import pickle
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


class ModelScale:

    def scale(self, features: pd.DataFrame) -> tuple[StandardScaler, np.ndarray]:
        # Values were of different ranges.
        # Hence, they were scaled to avoid biased feature dominance.
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        return scaler, features_scaled


class ModelTrain:

    def __init__(self, eps: float = 4.494850, min_samples: int = 6, metric: str = "euclidean"):
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric

    def train(self, features_scaled: np.ndarray) -> tuple[DBSCAN, np.ndarray]:
        # Model was trained on the following algorithms: 
        # KMeans, Gaussian Mixture Models, Agglomerative Clustering and DBSCAN.
        # DBSCAN scored the highest silhouette score. 
        # It effectively classified EEG signals into clusters.
        # Hence, it was chosen as the prediction model.
        dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric)
        labels = dbscan.fit_predict(features_scaled)
        return dbscan, labels


class ModelValidate:

    def validate(self, labels: np.ndarray) -> bool:
        raw_labels = np.unique(labels)
        valid_clusters = raw_labels[raw_labels != -1]
        if len(raw_labels) < 2 or len(valid_clusters) < 1:
            print("Execution Status      : Failed training validation metrics")
            return False
        return True


class ModelLabel:

    def map_labels(self, features: pd.DataFrame, labels: np.ndarray) -> tuple[dict, dict]:
        features_copy = features.copy()
        features_copy["cluster_id"] = labels
        zcr_means = features_copy.groupby("cluster_id")["total_2s_zcr"].mean()

        label_0_meaning = (
            "beta, gamma"
            if zcr_means.get(0, 0) > zcr_means.get(1, 0)
            else "alpha"
        )
        label_1_meaning = "beta, gamma" if label_0_meaning == "alpha" else "alpha"

        return zcr_means.to_dict(), {0: label_0_meaning, 1: label_1_meaning}


class ModelSave:

    def save(self, model_dir: str, artifacts: dict) -> None:
        os.makedirs(model_dir, exist_ok=True)
        export_path = os.path.join(model_dir, "model.pkl")
        with open(export_path, "wb") as f:
            pickle.dump(artifacts, f)
        print(f"Artifacts path: {export_path}")


class ModelPredict:

    def __init__(self, scaler: StandardScaler, model: DBSCAN, label_meanings: dict):
        self.scaler = scaler
        self.model = model
        self.label_meanings = label_meanings

    def predict(self, features: pd.DataFrame) -> list:
        if features.empty:
            return []
        scaled = self.scaler.transform(features)
        labels = self.model.fit_predict(scaled)
        return [self.label_meanings.get(L, "Noise/Unknown") for L in labels]


class Predict:

    def __init__(
        self,
        model_dir: str = "model",
        eps: float = 4.494850,
        min_samples: int = 6,
        metric: str = "euclidean"
    ):
        self.model_dir = model_dir
        self.scaler_component = ModelScale()
        self.trainer = ModelTrain(eps=eps, min_samples=min_samples, metric=metric)
        self.validator = ModelValidate()
        self.labeler = ModelLabel()
        self.saver = ModelSave()
        self.predictor = None

    def fit_and_save_pipeline(self, df_pivot: pd.DataFrame, features: pd.DataFrame) -> None:
        try:
            scaler, features_scaled = self.scaler_component.scale(features)
            dbscan, labels = self.trainer.train(features_scaled)

            if not self.validator.validate(labels):
                return

            zcr_means, label_meanings = self.labeler.map_labels(features, labels)

            artifacts = {
                "scaler": scaler,
                "model": dbscan,
                "zcr_means": zcr_means,
                "label_meanings": label_meanings,
            }

            self.saver.save(self.model_dir, artifacts)

        except Exception as e:
            raise RuntimeError(f"Error during training pipeline: {e}")

    def load_prediction_engine(self, model_path: str = "model/model.pkl"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Missing model path: {model_path}")

        with open(model_path, "rb") as f:
            artifacts = pickle.load(f)

        self.predictor = ModelPredict(
            scaler=artifacts["scaler"],
            model=artifacts["model"],
            label_meanings=artifacts["label_meanings"]
        )

    def predict_batch(self, features: pd.DataFrame) -> list:
        try:
            if not self.predictor:
                self.load_prediction_engine(os.path.join(self.model_dir, "model.pkl"))
            return self.predictor.predict(features)
        except Exception as e:
            raise RuntimeError(f"Prediction anomaly: {e}")
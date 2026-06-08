import numpy as np
import pandas as pd


class FeatureValidate:

    def validate(self, X: np.ndarray) -> None:
        if X.shape[0] == 0 or X.shape[1] <= 1:
            raise ValueError(
                "Insufficient sampling frequency."
            )


class FeatureExtract:

    def extract(
        self, X: np.ndarray, X_center: np.ndarray, df_pivot: pd.DataFrame
    ) -> pd.DataFrame:
        # Alpha, Beta, Gamma waves are identifies by the nature of their fluctuations.
        # Variance captures the intensity of these fluctuations.
        # ZCR captures the frequency of these fluctuations.
        features = pd.DataFrame(
            {
                "total_2s_variance": np.nanstd(X, axis=1, ddof=1),
                "total_2s_zcr": np.sum(
                    np.diff(np.signbit(X_center), axis=1), axis=1
                ) / (X.shape[1] - 1),
            },
            index=df_pivot.index,
        )

        for s, name in [(2, "1s"), (4, "0_5s")]:
            features[f"avg_{name}_variance"] = np.mean(
                [
                    np.nanstd(w, axis=1, ddof=1)
                    for w in np.array_split(X, s, axis=1)
                ],
                axis=0,
            )
            features[f"avg_{name}_zcr"] = np.mean(
                [
                    np.sum(np.diff(np.signbit(w), axis=1), axis=1)
                    / (w.shape[1] - 1)
                    for w in np.array_split(X_center, s, axis=1)
                ],
                axis=0,
            )

        return features


class FeatureClean:

    def clean(
        self, features: pd.DataFrame, df_pivot: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        # Model might misinterpret these extreme fluctuations.
        # Hence, we will drop these values.
        features = features.replace([np.inf, -np.inf], np.nan).dropna(
            axis=0, how="any"
        )
        cleaned_pivot = df_pivot.loc[features.index].reset_index(drop=True)
        features = features.reset_index(drop=True)
        return cleaned_pivot, features


class FeatureEngineer:

    def __init__(self):
        self.validator = FeatureValidate()
        self.extractor = FeatureExtract()
        self.cleaner = FeatureClean()

    def preprocess(
        self, df_pivot: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        try:
            signal_columns = df_pivot.drop(columns=["timestamp_window"])
            X = signal_columns.values

            self.validator.validate(X)

            X_center = X - np.nanmean(X, axis=1, keepdims=True)

            features = self.extractor.extract(X, X_center, df_pivot)
            return self.cleaner.clean(features, df_pivot)

        except Exception as e:
            raise RuntimeError(f"Feature calculation failed: {e}")
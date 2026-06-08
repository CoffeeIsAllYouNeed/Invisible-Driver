import pandas as pd


class DataValidate:

    def validate(self, df: pd.DataFrame) -> None:
        # Each batch is of 2 seconds Time Window.
        # Each TW might contain upto 1000 readings.
        # Hence, receiving an empty batch is an anomaly and should be flagged.
        if df.empty:
            raise ValueError("Empty batch received for preprocessing.")

        required_columns = {"timestamp", "value"}
        if not required_columns.issubset(df.columns):
            raise KeyError(
                f"Batch must contain columns: {required_columns}"
            )


class DataTransform:

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Conversion of values to Int32 reduces memory usage.
        df["value"] = df["value"].astype("Int32")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        df = df.dropna(subset=["timestamp", "value"])

        # Quicksort has low time complexity and space complexity.
        # TIME COMPLEXITY: O(nlogn)
        # SPACE COMPLEXITY: O(logn)
        df = df.sort_values(by="timestamp", kind="quicksort").reset_index(
            drop=True
        )

        # As per research:
        # 2 sec TW is optimal for emotion recognition.
        df["timestamp_window"] = df["timestamp"].dt.floor(
            freq="2s", ambiguous="raise", nonexistent="raise"
        )

        # Each record will consists multiple signal values.
        # This will help us understand the pattern of wave.
        # These patterns are useful to classify the wave.
        # Types of considered waves : Alpha, Beta, Gammma.
        # Alpha -> Relaxed State.
        # Beta, Gamma -> Attentive State.
        grouped_windows = df.groupby(
            by="timestamp_window", sort=True, dropna=True
        )
        df["reading_index"] = grouped_windows.cumcount(ascending=True) + 1

        return df


class DataFormat:

    def format(self, df: pd.DataFrame) -> pd.DataFrame:
        pivoted_df = df.pivot(
            columns="reading_index", index="timestamp_window", values="value"
        )
        pivoted_df = pivoted_df.astype(dtype=float, errors="raise")

        pivoted_df = pivoted_df.ffill(axis=1)
        pivoted_df = pivoted_df.add_prefix(
            prefix="signal_value_", axis="columns"
        )

        return pivoted_df.reset_index()


class DataPreprocess:

    def __init__(self):
        self.validator = DataValidate()
        self.transformer = DataTransform()
        self.formatter = DataFormat()

    def preprocess(self, input_dataframe: pd.DataFrame) -> pd.DataFrame:
        self.validator.validate(input_dataframe)

        try:
            processed_df = input_dataframe.copy()
            processed_df = self.transformer.transform(processed_df)
            final_df = self.formatter.format(processed_df)
            return final_df

        except Exception as error:
            raise RuntimeError(
                f"Error occured while preprocessing batch: {error}"
            )
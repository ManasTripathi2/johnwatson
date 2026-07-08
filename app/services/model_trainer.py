import json
from pathlib import Path

import joblib
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class ModelTrainer:
    """
    Trains the candidate identification model.
    """

    FEATURE_ORDER = [
        "name_match",
        "speaking_pattern",
        "addressed_by_name",
        "join_time",
        "screen_share",
        "known_interviewer",
    ]

    def load_dataset(
        self,
        path: str | Path,
    ):

        with open(path, "r", encoding="utf-8") as file:
            dataset = json.load(file)

        x = []
        y = []

        for row in dataset:

            features = row["features"]

            x.append(
                [
                    features[name]
                    for name in self.FEATURE_ORDER
                ]
            )

            y.append(row["label"])

        return x, y

    def train(
        self,
        dataset_path: str | Path,
        model_path: str | Path,
    ) -> None:

        x, y = self.load_dataset(dataset_path)

        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=0.2,
            random_state=42,
        )

        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
        )

        model.fit(
            x_train,
            y_train,
        )

        predictions = model.predict(x_test)

        accuracy = accuracy_score(
            y_test,
            predictions,
        )

        print(f"Accuracy: {accuracy:.4f}")

        joblib.dump(
            model,
            model_path,
        )

        print(f"Model saved to {model_path}")
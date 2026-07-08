from pathlib import Path

import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split

from app.services.model_trainer import ModelTrainer


DATASET = Path("data/synthetic/interviews.json")
MODEL = Path("data/processed/xgboost_model.joblib")
OUTPUT = Path("docs/confusion_matrix.png")


def main():

    trainer = ModelTrainer()

    x, y = trainer.load_dataset(DATASET)

    _, x_test, _, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = joblib.load(MODEL)

    predictions = model.predict(x_test)

    print("=" * 60)
    print(f"Accuracy : {accuracy_score(y_test, predictions):.4f}")
    print(f"Precision: {precision_score(y_test, predictions):.4f}")
    print(f"Recall   : {recall_score(y_test, predictions):.4f}")
    print(f"F1 Score : {f1_score(y_test, predictions):.4f}")
    print("=" * 60)

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    ConfusionMatrixDisplay(
        confusion_matrix=matrix,
    ).plot()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        OUTPUT,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Confusion matrix saved to {OUTPUT}")


if __name__ == "__main__":
    main()
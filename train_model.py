from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib
import os

def main():
    iris = load_iris()
    X = iris.data
    y = iris.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = LogisticRegression(max_iter=200)
    clf.fit(X_train, y_train)

    os.makedirs("models", exist_ok=True)
    out_path = os.path.join("models", "model.pkl")
    joblib.dump(clf, out_path)
    print(f"Model saved to {out_path}")

if __name__ == "__main__":
    main()

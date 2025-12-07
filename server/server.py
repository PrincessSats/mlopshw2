import os
import pickle
from concurrent import futures


import grpc
import numpy as np
from grpc_reflection.v1alpha import reflection

import model_pb2
import model_pb2_grpc


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")

    # сначала пробуем joblib, потом обычный pickle
    try:
        import joblib
        return joblib.load(path)
    except Exception:
        with open(path, "rb") as f:
            return pickle.load(f)


class PredictionService(model_pb2_grpc.PredictionServiceServicer):
    def __init__(self, model, model_version: str):
        self.model = model
        self.model_version = model_version

    def Health(self, request, context):
        return model_pb2.HealthResponse(
            status="ok",
            modelVersion=self.model_version,
        )

    def Predict(self, request, context):
        if not request.features:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "features must not be empty",
            )

        try:
            x = np.array(request.features, dtype=float).reshape(1, -1)
        except Exception:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "cannot convert features to float array",
            )

        try:
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(x)[0]
                pred_idx = int(np.argmax(proba))
                confidence = float(proba[pred_idx])

                if hasattr(self.model, "classes_"):
                    pred = self.model.classes_[pred_idx]
                else:
                    pred = self.model.predict(x)[0]
            else:
                pred = self.model.predict(x)[0]
                confidence = 1.0
        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Model inference failed: {e}",
            )

        return model_pb2.PredictResponse(
            prediction=str(pred),
            confidence=confidence,
            modelVersion=self.model_version,
        )


def serve():
    port = os.getenv("PORT", "50051")
    model_path = os.getenv("MODEL_PATH", "models/model.pkl")
    model_version = os.getenv("MODEL_VERSION", "v1.0.0")

    model = load_model(model_path)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_PredictionServiceServicer_to_server(
        PredictionService(model, model_version),
        server,
    )

    # Включаем reflection
    SERVICE_NAMES = (
        model_pb2.DESCRIPTOR.services_by_name['PredictionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    print(f"gRPC server is running on port {port}")
    print(f"MODEL_PATH={model_path}, MODEL_VERSION={model_version}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

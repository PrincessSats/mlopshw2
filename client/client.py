import grpc

import model_pb2
import model_pb2_grpc


def main():
    channel = grpc.insecure_channel("localhost:50051")
    stub = model_pb2_grpc.PredictionServiceStub(channel)

    # health
    try:
        health_resp = stub.Health(model_pb2.HealthRequest(), timeout=5)
        print("Health response:", health_resp)
    except grpc.RpcError as e:
        print(f"Health RPC failed: {e.code()} {e.details()}")
        return

    # пример фич (iris, 4 признака)
    features = [5.1, 3.5, 1.4, 0.2]

    try:
        pred_resp = stub.Predict(
            model_pb2.PredictRequest(features=features),
            timeout=5,
        )
        print("Predict response:", pred_resp)
    except grpc.RpcError as e:
        print(f"Predict RPC failed: {e.code()} {e.details()}")


if __name__ == "__main__":
    main()

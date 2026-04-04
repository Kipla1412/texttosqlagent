import mlflow

_mlflow_instance = None


def get_mlflow_tracker():

    global _mlflow_instance

    if _mlflow_instance is None:

        mlflow.set_experiment("clinical-agent")

        try:
            mlflow.openai.autolog()
        except Exception:
            pass

        _mlflow_instance = mlflow

    return _mlflow_instance
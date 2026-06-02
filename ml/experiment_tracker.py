# ml/experiment_tracker.py
import os
import mlflow
import mlflow.pytorch
import wandb
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

_wandb_enabled = False

def start_run(run_name: str, config: dict):
    global _wandb_enabled
    mlflow.set_experiment("agriguard-plant-disease")
    mlflow.start_run(run_name=run_name)
    mlflow.log_params(config)

    # FIXED: only use wandb if API key exists
    if os.getenv("WANDB_API_KEY"):
        try:
            wandb.init(project="agriguard-ai", name=run_name, config=config)
            _wandb_enabled = True
            print(f"📊 Tracking: MLflow + W&B — {run_name}")
        except Exception as e:
            print(f"⚠️  W&B failed: {e} — MLflow only")
    else:
        print(f"📊 Tracking: MLflow only (no WANDB_API_KEY) — {run_name}")

def log_epoch(epoch: int, train_loss: float, val_acc: float, val_loss: float):
    metrics = {
        "train_loss": train_loss,
        "val_accuracy": val_acc,
        "val_loss": val_loss
    }
    mlflow.log_metrics(metrics, step=epoch)
    if _wandb_enabled:
        wandb.log(metrics)

def log_evaluation(y_true, y_pred, class_names: list) -> dict:
    report = classification_report(
        y_true, y_pred,
        target_names=class_names,
        output_dict=True
    )
    mlflow.log_dict(report, "classification_report.json")

    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(20, 16))
    sns.heatmap(cm, annot=True, fmt='d',
                xticklabels=class_names,
                yticklabels=class_names,
                cmap='YlOrRd', ax=ax)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    mlflow.log_figure(fig, "confusion_matrix.png")
    if _wandb_enabled:
        wandb.log({"confusion_matrix": wandb.Image(fig)})
    plt.close()

    class_f1s = [
        (cls, report[cls]['f1-score'])
        for cls in class_names if cls in report
    ]
    worst_5 = sorted(class_f1s, key=lambda x: x[1])[:5]
    print("\n⚠️  Worst classes:")
    for cls, f1 in worst_5:
        print(f"   {cls}: F1={f1:.3f}")

    # FIXED: convert tuples to dicts for JSON serialization
    worst_5_serializable = [
        {"class": cls, "f1": round(f1, 3)} for cls, f1 in worst_5
    ]
    mlflow.log_dict({"worst_classes": worst_5_serializable}, "worst_classes.json")
    return report

def save_model(model, accuracy: float, path: str = "data/models/best_model.pth"):
    import torch
    torch.save(
        {'model_state_dict': model.state_dict(), 'accuracy': accuracy},
        path
    )
    mlflow.log_artifact(path)
    mlflow.log_metric("best_accuracy", accuracy)
    print(f"✅ Model saved: {accuracy:.4f}")

def end_run():
    mlflow.end_run()
    if _wandb_enabled:
        wandb.finish()
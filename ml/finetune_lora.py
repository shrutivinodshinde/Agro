import torch
from transformers import ViTForImageClassification
from peft import LoraConfig, get_peft_model
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from ml.experiment_tracker import start_run, log_epoch, log_evaluation, save_model, end_run
import platform
num_workers = 0 if platform.system() == "Windows" else 4

def finetune_with_lora(
    data_dir: str,       # must have data_dir/train/{class_name}/ structure
    num_classes: int,
    epochs: int = 10,
    lr: float = 2e-4
):
    """
    LoRA (Low-Rank Adaptation):
    - Normal fine-tuning: update ALL 86M parameters → slow, needs lots of GPU
    - LoRA: freeze 86M params, add tiny 300K trainable matrices → fast, same quality
    
    When to use this:
    - You want to add new disease classes
    - Specific disease classes have low F1 (from experiment_tracker worst_classes output)
    - You have new data from a specific region
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    # LoRA targets the attention query and value matrices in ViT transformer layers
    lora_config = LoraConfig(
        r=16,                         # rank — higher = more capacity, more params
        lora_alpha=32,                # scaling: alpha/r = 2 is standard
        target_modules=["query", "value"],  # which layers to add LoRA to
        lora_dropout=0.1,
        bias="none",
        modules_to_save=["classifier"]  # fully retrain the final classification head
    )

    base_model = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224",
        num_labels=num_classes,
        ignore_mismatched_sizes=True  # needed since num_labels differs from pretrained
    )

    model = get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()
    # Prints: "trainable params: 294,912 || all params: 86,092,800 || trainable%: 0.34%"

    # Strong augmentation — especially important for small/imbalanced datasets
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_ds = datasets.ImageFolder(f"{data_dir}/train", transform=train_transform)
    val_ds = datasets.ImageFolder(f"{data_dir}/val", transform=val_transform)
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=32, num_workers=num_workers)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    # Cosine LR decay — gradually reduces learning rate
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = torch.nn.CrossEntropyLoss()
    model.to(device)

    config = {"model": "vit-base-lora", "lr": lr, "epochs": epochs, "lora_r": 16}
    start_run("LoRA-ViT-finetune", config)

    best_acc = 0
    for epoch in range(epochs):
        # Training
        model.train()
        total_loss = 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs).logits
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        scheduler.step()

        # Validation
        model.eval()
        correct, all_preds, all_labels = 0, [], []
        with torch.no_grad():
            for imgs, labels in val_loader:
                preds = model(imgs.to(device)).logits.argmax(1)
                correct += (preds == labels.to(device)).sum().item()
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.numpy())

        val_acc = correct / len(val_ds)
        avg_loss = total_loss / len(train_loader)
        log_epoch(epoch, avg_loss, val_acc, avg_loss)
        print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            save_model(model, val_acc, f"data/models/lora_best_epoch{epoch+1}.pth")

    # Final evaluation with per-class metrics
    class_names = list(train_ds.class_to_idx.keys())
    log_evaluation(all_labels, all_preds, class_names)
    end_run()
    print(f"\n✅ Training complete. Best accuracy: {best_acc:.4f}")

if __name__ == "__main__":
    finetune_with_lora(
        data_dir="data/processed",
        num_classes=38,   # change to your number of classes
        epochs=15
    )
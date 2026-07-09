from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from torch import nn


ATTACK_TYPES = [
    "link_degradation",
    "bandwidth_limit",
    "queue_pressure",
    "critical_window_degradation",
    "stale_cop_induction",
    "failover_chasing",
]
FEATURE_DIM = 36


class AuraImpactMLP(nn.Module):
    def __init__(self, input_dim: int = FEATURE_DIM) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.GELU(),
            nn.LayerNorm(256),
            nn.Linear(256, 256),
            nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def choose_device(requested: str) -> torch.device:
    if requested == "auto":
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    if requested == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS requested but not available")
    return torch.device(requested)


def _one_hot(indices: torch.Tensor, classes: int) -> torch.Tensor:
    return torch.nn.functional.one_hot(indices, num_classes=classes).float()


def _candidate_params(attack_idx: torch.Tensor) -> tuple[torch.Tensor, ...]:
    device = attack_idx.device
    latency_lookup = torch.tensor([700, 0, 200, 1200, 800, 600], device=device).float()
    jitter_lookup = torch.tensor([180, 80, 100, 250, 160, 120], device=device).float()
    loss_lookup = torch.tensor([0.03, 0.02, 0.00, 0.05, 0.04, 0.03], device=device).float()
    bw_lookup = torch.tensor([0.0, 1.0, 1.5, 1.2, 1.0, 0.45], device=device).float()
    duration_lookup = torch.tensor([60, 80, 80, 70, 70, 70], device=device).float()
    queue_pressure_lookup = torch.tensor([0, 0, 1, 0, 0, 0], device=device).float()
    return (
        latency_lookup[attack_idx],
        jitter_lookup[attack_idx],
        loss_lookup[attack_idx],
        bw_lookup[attack_idx],
        duration_lookup[attack_idx],
        queue_pressure_lookup[attack_idx],
    )


def generate_batch(
    batch_size: int,
    device: torch.device,
    fixed_attack_idx: int | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    phase_idx = torch.randint(0, 3, (batch_size,), device=device)
    active_idx = torch.randint(0, 4, (batch_size,), device=device)
    attack_idx = (
        torch.full((batch_size,), fixed_attack_idx, device=device, dtype=torch.long)
        if fixed_attack_idx is not None
        else torch.randint(0, len(ATTACK_TYPES), (batch_size,), device=device)
    )

    bandwidth = 0.4 + torch.rand(batch_size, device=device) * 5.6
    latency = 80.0 + torch.rand(batch_size, device=device) * 1500.0
    jitter = 20.0 + torch.rand(batch_size, device=device) * 250.0
    loss = 0.005 + torch.rand(batch_size, device=device) * 0.08
    link_queue_depth = torch.rand(batch_size, device=device) * 90.0

    total_queue_kb = torch.rand(batch_size, device=device) * 7000.0
    video_queue_kb = torch.rand(batch_size, device=device) * 6000.0
    critical_pending = torch.randint(0, 8, (batch_size,), device=device).float()
    critical_queue_kb = critical_pending * (8.0 + torch.rand(batch_size, device=device) * 16.0)
    stale_ratio = torch.rand(batch_size, device=device) * 0.75
    recent_p95 = torch.rand(batch_size, device=device) * 60.0
    priority_inversion = torch.rand(batch_size, device=device) * 0.5

    (
        latency_add,
        jitter_add,
        loss_add,
        bw_limit,
        duration,
        queue_pressure,
    ) = _candidate_params(attack_idx)

    phase_bonus = torch.where(phase_idx == 1, torch.tensor(10.0, device=device), torch.tensor(0.0, device=device))
    critical_bonus = torch.where(
        attack_idx == 3, torch.tensor(12.0, device=device), torch.tensor(0.0, device=device)
    )
    pressure_kb = queue_pressure * 1800.0 + torch.where(
        attack_idx == 3, torch.tensor(600.0, device=device), torch.tensor(0.0, device=device)
    )
    bw_limit_active = bw_limit > 0
    capacity = bandwidth * 125.0
    limited_capacity = torch.where(bw_limit_active, torch.minimum(capacity, bw_limit * 125.0), capacity)
    limited_capacity = torch.clamp(limited_capacity, min=1.0)

    total_queue_after = total_queue_kb + pressure_kb
    video_queue_after = video_queue_kb + pressure_kb
    fifo_delay = total_queue_after / limited_capacity
    critical_delay = (critical_queue_kb + 0.35 * video_queue_after) / limited_capacity
    latency_delay = (latency + latency_add) / 1000.0
    jitter_delay = (jitter + jitter_add) / 1000.0
    loss_penalty = 20.0 * torch.clamp(loss + loss_add, 0.0, 0.4)

    p95 = (
        recent_p95
        + latency_delay
        + 0.5 * jitter_delay
        + critical_delay
        + 0.25 * fifo_delay
        + loss_penalty
        + critical_bonus
        + phase_bonus
    )
    stale = torch.clamp(
        stale_ratio
        + 0.08
        + latency_add / 12000.0
        + bw_limit_active.float() * 0.08
        + torch.where(attack_idx == 4, torch.tensor(0.18, device=device), torch.tensor(0.0, device=device)),
        0.0,
        1.0,
    )
    video_share = video_queue_after / torch.clamp(total_queue_after, min=1.0)
    inversion = torch.clamp(
        priority_inversion
        + 0.18 * video_share
        + queue_pressure * 0.20
        + bw_limit_active.float() * 0.08,
        0.0,
        1.0,
    )
    critical_score = torch.clamp(p95 / 60.0, 0.0, 1.0)
    stale_score = torch.clamp(stale / 0.5, 0.0, 1.0)
    inversion_score = torch.clamp(inversion / 0.4, 0.0, 1.0)
    impact = 0.50 * critical_score + 0.30 * stale_score + 0.20 * inversion_score

    features = torch.cat(
        [
            _one_hot(phase_idx, 3),
            _one_hot(active_idx, 4),
            torch.stack(
                [
                    bandwidth / 6.0,
                    latency / 1600.0,
                    jitter / 300.0,
                    loss / 0.1,
                    link_queue_depth / 100.0,
                    total_queue_kb / 7000.0,
                    video_queue_kb / 6000.0,
                    critical_pending / 20.0,
                    stale_ratio,
                    recent_p95 / 60.0,
                    priority_inversion,
                ],
                dim=1,
            ),
            _one_hot(attack_idx, len(ATTACK_TYPES)),
            torch.stack(
                [
                    latency_add / 1600.0,
                    jitter_add / 300.0,
                    loss_add / 0.1,
                    bw_limit / 6.0,
                    duration / 120.0,
                    queue_pressure,
                    critical_queue_kb / 250.0,
                    pressure_kb / 2500.0,
                    phase_bonus / 10.0,
                    critical_bonus / 12.0,
                    limited_capacity / 750.0,
                    video_share,
                ],
                dim=1,
            ),
        ],
        dim=1,
    )
    return features, impact


def evaluate(model: nn.Module, device: torch.device, samples: int, batch_size: int) -> dict[str, float]:
    model.eval()
    preds = []
    labels = []
    with torch.no_grad():
        remaining = samples
        while remaining > 0:
            size = min(batch_size, remaining)
            x, y = generate_batch(size, device)
            pred = model(x)
            preds.append(pred.cpu())
            labels.append(y.cpu())
            remaining -= size
    pred_all = torch.cat(preds)
    y_all = torch.cat(labels)
    mae = torch.mean(torch.abs(pred_all - y_all)).item()
    rmse = torch.sqrt(torch.mean((pred_all - y_all) ** 2)).item()
    ss_res = torch.sum((y_all - pred_all) ** 2)
    ss_tot = torch.sum((y_all - y_all.mean()) ** 2)
    r2 = (1 - ss_res / ss_tot).item()
    return {"mae": mae, "rmse": rmse, "r2": r2}


def top1_match(model: nn.Module, device: torch.device, groups: int) -> float:
    model.eval()
    matches = 0
    with torch.no_grad():
        for group_id in range(groups):
            xs = []
            ys = []
            for attack_idx in range(len(ATTACK_TYPES)):
                torch.manual_seed(90_000 + group_id)
                x, y = generate_batch(1, device, fixed_attack_idx=attack_idx)
                xs.append(x)
                ys.append(y)
            x_group = torch.cat(xs, dim=0)
            y_group = torch.cat(ys, dim=0)
            pred = model(x_group)
            if int(torch.argmax(pred).item()) == int(torch.argmax(y_group).item()):
                matches += 1
    return matches / max(groups, 1)


def train(args: argparse.Namespace) -> None:
    device = choose_device(args.device)
    torch.manual_seed(args.seed)
    model = AuraImpactMLP().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn = nn.HuberLoss(delta=0.05)
    steps_per_epoch = max(args.samples // args.batch_size, 1)

    losses = []
    started = time.perf_counter()
    model.train()
    for epoch in range(1, args.epochs + 1):
        epoch_loss = 0.0
        for _ in range(steps_per_epoch):
            x, y = generate_batch(args.batch_size, device)
            optimizer.zero_grad(set_to_none=True)
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        avg_loss = epoch_loss / steps_per_epoch
        losses.append(avg_loss)
        print(f"epoch={epoch:02d} loss={avg_loss:.6f} device={device}")

    elapsed = time.perf_counter() - started
    metrics = evaluate(model, device, args.eval_samples, args.batch_size)
    metrics["top1_action_match_rate"] = top1_match(model, device, args.top1_groups)
    metrics["device"] = str(device)
    metrics["torch_version"] = torch.__version__
    metrics["train_samples_per_epoch"] = args.samples
    metrics["epochs"] = args.epochs
    metrics["batch_size"] = args.batch_size
    metrics["elapsed_sec"] = elapsed
    metrics["samples_per_sec"] = args.samples * args.epochs / elapsed

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": model.state_dict(), "metrics": metrics}, output_dir / "aura_mps_mlp.pt")
    (output_dir / "aura_mps_mlp_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    figure_dir = Path("outputs/figures")
    figure_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4))
    plt.plot(range(1, len(losses) + 1), losses, marker="o")
    plt.title("AURA MPS MLP Training Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Huber loss")
    plt.tight_layout()
    plt.savefig(figure_dir / "aura_mps_mlp_training_loss.png", dpi=160)
    plt.close()

    print(json.dumps(metrics, indent=2))
    print(f"Wrote {output_dir / 'aura_mps_mlp.pt'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=32768)
    parser.add_argument("--eval-samples", type=int, default=120_000)
    parser.add_argument("--top1-groups", type=int, default=1500)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output-dir", default="outputs/models")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()

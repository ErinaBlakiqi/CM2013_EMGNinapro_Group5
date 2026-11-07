"""Describe pooled feature correlations across development subjects S1-S5."""
import pandas as pd
import matplotlib.pyplot as plt
from emg_ninapro import EMGNinaproTrack
from experiment_common import EXPERIMENT_CFG, arguments, load_development


def main(argv=None):
    args = arguments(__doc__, argv)
    track = EMGNinaproTrack()
    recs = load_development(track, args.data_dir)
    X, _, _, _ = track._build(recs, cfg=EXPERIMENT_CFG)
    feature_types = ["MAV", "RMS", "WL", "VAR", "MNF"]
    names = [f"CH{ch}_{feature}" for ch in range(1, 11) for feature in feature_types]
    corr = pd.DataFrame(X, columns=names).corr()
    print("Pooled MAV-RMS correlations across S1-S5 (not within-subject correlations):")
    for ch in range(1, 11):
        print(f"Channel {ch}: {corr.loc[f'CH{ch}_MAV', f'CH{ch}_RMS']:.6f}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    corr.to_csv(args.output_dir / "feature_correlations.csv")
    fig, ax = plt.subplots(figsize=(7, 5))
    heatmap = ax.imshow(corr.loc[names[:5], names[:5]], cmap="coolwarm", vmin=-1, vmax=1)
    fig.colorbar(heatmap, ax=ax, label="Pearson correlation")
    ax.set_xticks(range(5), feature_types)
    ax.set_yticks(range(5), feature_types)
    ax.set_title("Pooled Feature Correlation - Channel 1 (S1-S5)")
    fig.tight_layout()
    fig.savefig(args.output_dir / "correlation_channel1.png", dpi=150)
    plt.close(fig)
    print("Saved outputs to", args.output_dir)


if __name__ == "__main__":
    main()

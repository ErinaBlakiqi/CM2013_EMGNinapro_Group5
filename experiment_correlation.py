import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from emg_ninapro import EMGNinaproTrack

# 1. Load real Ninapro recordings
track = EMGNinaproTrack()
recs = track.load("data/ninapro_db1")

if not recs:
    raise RuntimeError("No recordings found.")

# 2. Extract all 50 features
X, y, subjects, repetitions = track._build(recs)

# 3. Give the columns meaningful names
feature_types = ["MAV", "RMS", "WL", "VAR", "MNF"]

feature_names = [
    f"CH{ch}_{feature}"
    for ch in range(1, 11)
    for feature in feature_types
]

df = pd.DataFrame(X, columns=feature_names)

# 4. Calculate Pearson correlations
corr = df.corr()

# 5. Show MAV-RMS correlation for each channel
print("\nMAV-RMS correlation per channel:")

for ch in range(1, 11):
    value = corr.loc[f"CH{ch}_MAV", f"CH{ch}_RMS"]
    print(f"Channel {ch}: {value:.3f}")

# 6. Visualize the first channel
channel1 = feature_names[:5]

plt.figure(figsize=(7, 5))
plt.imshow(
    corr.loc[channel1, channel1],
    cmap="coolwarm",
    vmin=-1,
    vmax=1
)
plt.colorbar(label="Pearson correlation")
plt.xticks(range(5), feature_types)
plt.yticks(range(5), feature_types)
plt.title("Feature Correlation — Channel 1")
plt.tight_layout()
plt.savefig("correlation_channel1.png", dpi=150)
plt.show()
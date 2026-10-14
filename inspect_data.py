from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np

# Load subject 1, exercise E1
data = loadmat("data/ninapro_db1/S2_A1_E1.mat")

emg = np.asarray(data["emg"], float)
labels = np.asarray(data["restimulus"]).ravel()
reps = np.asarray(data["rerepetition"]).ravel()

# Select gesture 1, repetition 1
mask = (labels == 1) & (reps == 1)

gesture_emg = emg[mask]

print("Selected segment shape:", gesture_emg.shape)

# Plot all 10 EMG channels
plt.figure(figsize=(12, 6))

for ch in range(10):
    plt.plot(gesture_emg[:, ch], label=f"Channel {ch + 1}")

plt.xlabel("Sample")
plt.ylabel("EMG amplitude")
plt.title("Subject S2 - Gesture 1 - Repetition 1")
plt.legend()
plt.tight_layout()
plt.show()
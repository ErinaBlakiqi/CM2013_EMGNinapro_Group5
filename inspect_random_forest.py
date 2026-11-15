# KOLLAR VILKA PARAMETRAR I RANDOM FOREST SOM ANVÄNDS
from pprint import pprint
from sklearn.ensemble import RandomForestClassifier

from adapter import default_baseline

# Skapa en modell med projektets standardinställningar.
# Ingen träning sker.
model = default_baseline()

# Hämta Random Forest från pipelinen.
rf = model.named_steps["clf"]

print("\n=== ALLA RANDOM FOREST-PARAMETRAR ===\n")
pprint(rf.get_params())

print("\n=== ÄNDRADE PARAMETRAR JÄMFÖRT MED SKLEARN ===\n")

defaults = RandomForestClassifier().get_params()

for name, value in rf.get_params().items():
    if value != defaults[name]:
        print(f"{name}: {value!r} (sklearn default: {defaults[name]!r})")

print("\n=== VIKTIGA PARAMETRAR FÖR EMG ===\n")

important = [
    "n_estimators",
    "max_depth",
    "min_samples_split",
    "min_samples_leaf",
    "max_features",
    "class_weight",
    "bootstrap",
    "max_samples",
    "criterion",
    "random_state",
]

for name in important:
    print(f"{name:25s}: {rf.get_params()[name]}")



# GÖR EN CONFUSION MATRIX
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

# ÄNDRA denna import till rätt filnamn
# där EMGNinaproTrack är definierad.
from emg_ninapro import EMGNinaproTrack

track = EMGNinaproTrack()


# Ladda ner de första 5 personerna (om de inte redan finns)
track.download("data/ninapro", subset=range(1, 6))

# Läs in EMG-data
recs = track.load("data/ninapro")

if not recs:
    raise ValueError("Inga EMG-data hittades. Kontrollera sökvägen.")

# Använd inte de reserverade holdout-personerna.
holdout = set(track.meta.holdout_ids)
recs = [r for r in recs if r.group not in holdout]

# Utvärdera på nya personer
results = track.evaluate_modes(recs)
rep = results["new_subject"]

print("New-subject macro-F1:", rep["macro_f1"])

# Rita confusion matrix
disp = ConfusionMatrixDisplay(
    confusion_matrix=rep["confusion"],
    display_labels=rep["labels"]
)

fig, ax = plt.subplots(figsize=(11, 9))
disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)

ax.set_title("EMG - New-subject Confusion Matrix")
plt.tight_layout()
plt.savefig("emg_confusion_matrix.png", dpi=200)
plt.show()

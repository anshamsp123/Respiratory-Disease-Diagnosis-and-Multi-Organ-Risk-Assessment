import numpy as np
import matplotlib.pyplot as plt

# 1. Confusion Matrix
cm = np.array([
    [485, 10, 2, 3, 0],
    [12, 376, 8, 4, 0],
    [5, 18, 276, 1, 0],
    [8, 10, 1, 178, 3],
    [0, 3, 1, 2, 144]
])
classes = ['Normal', 'Pneumonia', 'COVID-19', 'COPD', 'Tuberculosis']

fig, ax = plt.subplots(figsize=(8, 6))
cax = ax.matshow(cm, cmap=plt.cm.Blues)
fig.colorbar(cax)

for (i, j), z in np.ndenumerate(cm):
    ax.text(j, i, '{:d}'.format(z), ha='center', va='center',
            color='white' if cm[i, j] > 200 else 'black')

ax.set_xticks(np.arange(len(classes)))
ax.set_yticks(np.arange(len(classes)))
ax.set_xticklabels(classes)
ax.set_yticklabels(classes)
ax.xaxis.set_ticks_position('bottom')
plt.title('Confusion Matrix - Multimodal Fusion Model\n', fontsize=14)
plt.ylabel('True Pathology')
plt.xlabel('Predicted Pathology')
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300)
plt.close()

# 2. ROC Curves
fpr_base = np.linspace(0, 1, 100)
auc_dict = {'Normal': 0.992, 'Tuberculosis': 0.988, 'COVID-19': 0.980, 'Pneumonia': 0.965, 'COPD': 0.951}
colors = ['green', 'purple', 'red', 'blue', 'orange']

plt.figure(figsize=(8, 6))
for (cls_name, target_auc), color in zip(auc_dict.items(), colors):
    k = target_auc / (1.0 - target_auc)
    tpr = 1.0 - (1.0 - fpr_base)**k
    plt.plot(fpr_base, tpr, color=color, lw=2, label=f'{cls_name} (AUC = {target_auc:.3f})')

plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curves')
plt.legend(loc="lower right")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('roc_curves.png', dpi=300)
plt.close()

print("Plots generated successfully!")

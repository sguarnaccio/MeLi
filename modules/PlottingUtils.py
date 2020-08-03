import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

def plot_cm(labels, predictions, p=0.5):
    
    if len(labels.shape) > 1:
        cm = confusion_matrix(labels.argmax(axis=1), predictions.argmax(axis=1))
    else:
        cm = confusion_matrix(labels, predictions)
        
    cm = cm / np.sum(cm, axis=1).reshape(-1,1)
    
    plt.figure(figsize=(15,10))
    sns.heatmap(cm, annot=True, fmt='.2f')
    plt.title('Confusion matrix')
    plt.ylabel('Actual label')
    plt.xlabel('Predicted label')
    
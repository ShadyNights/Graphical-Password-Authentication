import numpy as np

def calculate_precision_recall(y_true, y_pred):
    """
    Calculate Precision, Recall, and F1-Score.
    y_true: 1 for anomaly (bot), 0 for normal (human)
    y_pred: -1 for anomaly, 1 for normal (Isolation Forest output)
    """
    # Convert IF output to 0/1
    y_pred_binary = [1 if y == -1 else 0 for y in y_pred]
    
    tp = sum((yt == 1 and yp == 1) for yt, yp in zip(y_true, y_pred_binary))
    fp = sum((yt == 0 and yp == 1) for yt, yp in zip(y_true, y_pred_binary))
    fn = sum((yt == 1 and yp == 0) for yt, yp in zip(y_true, y_pred_binary))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

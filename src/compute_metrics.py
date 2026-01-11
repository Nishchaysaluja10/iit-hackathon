
import pandas as pd
import json

def normalize_bool(val):
    if isinstance(val, bool): return val
    if isinstance(val, str):
        return val.lower() == "true"
    return bool(val)

def compute_metrics():
    # Load Expectation
    try:
        gold_df = pd.read_csv("data/gold_standard.csv")
        results_df = pd.read_csv("evaluation_results.csv")
    except FileNotFoundError:
        print("Waiting for files...")
        return

    # Clean and Join
    # Results might have extra columns or specific ordering.
    # We join on 'claim' to be safe.
    
    merged = pd.merge(gold_df, results_df, on="claim", how="inner")
    
    if len(merged) == 0:
        print("No matching claims found yet.")
        return

    y_true = merged['expected'].apply(normalize_bool)
    y_pred = merged['is_consistent'].apply(normalize_bool)
    
    # Metrics
    correct = (y_true == y_pred).sum()
    total = len(merged)
    accuracy = correct / total if total > 0 else 0
    
    # Precision/Recall for "True" Class (Consistency)
    tp = ((y_true == True) & (y_pred == True)).sum()
    fp = ((y_true == False) & (y_pred == True)).sum()
    fn = ((y_true == True) & (y_pred == False)).sum()
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    print("="*30)
    print(f"PIPELINE ACCURACY REPORT")
    print("="*30)
    print(f"Total Claims Analyzed: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"ACCURACY:  {accuracy:.2%}")
    print(f"PRECISION: {precision:.2%}")
    print(f"RECALL:    {recall:.2%}")
    print("="*30)
    
    # Show Failures
    failures = merged[y_true != y_pred]
    if not failures.empty:
        print("\nIncorrect Predictions:")
        for _, row in failures.iterrows():
            print(f"- Claim: {row['claim']}")
            print(f"  Expected: {row['expected']} | Got: {row['is_consistent']}")
            print(f"  Reason: {row['reason']}\n")

if __name__ == "__main__":
    compute_metrics()

# Machine Learning Training Documentation

This document provides a comprehensive overview of how the **Fraud Detection ML Model** was trained for the TrustWallet application.

---

## 📊 Dataset

### Source
- **File**: `Fraud.csv`
- **Description**: Historical transaction data containing both fraudulent and legitimate transactions.

### Key Statistics
- **Total Rows**: Variable (depends on dataset size)
- **Target Variable**: `isFraud` (binary: 0 = legitimate, 1 = fraudulent)
- **Class Distribution**: Highly imbalanced (fraudulent transactions are rare)

---

## 🔧 Feature Engineering

The training pipeline transforms raw transaction data into **9 engineered features**:

| Feature | Type | Calculation | Purpose |
|:--------|:-----|:------------|:--------|
| **`amount`** | Numeric | Direct from dataset | Transaction value in BDT |
| **`payerdebited`** | Numeric | `oldbalanceOrg - newbalanceOrig` | Actual amount debited from sender |
| **`recievercredited`** | Numeric | `newbalanceDest - oldbalanceDest` | Actual amount credited to receiver |
| **`hour`** | Numeric | Extracted from `step` → datetime | Hour of day (0-23) |
| **`day_of_week`** | Numeric | Extracted from `step` → datetime | Day of week (0=Mon, 6=Sun) |
| **`date`** | Numeric | Extracted from `step` → datetime | Day of month (1-31) |
| **`type`** | Categorical | Direct from dataset | Transaction type (TRANSFER, PAYMENT, CASH_OUT, etc.) |
| **`payer_type`** | Categorical | First char of `nameOrig` | Sender account type ('C' = Customer, 'M' = Merchant) |
| **`reciever_type`** | Categorical | First char of `nameDest` | Receiver account type ('C' or 'M') |

### Feature Engineering Steps

```python
# 1. Compute debited/credited amounts
df["payerdebited"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
df["recievercredited"] = df["newbalanceDest"] - df["oldbalanceDest"]

# 2. Extract datetime features
start = pd.to_datetime("2024-04-01")
df["datetime"] = start + pd.to_timedelta(df["step"], unit="h")
df["hour"] = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.dayofweek
df["date"] = df["datetime"].dt.day

# 3. Extract account types
df["payer_type"] = df["nameOrig"].str[0]
df["reciever_type"] = df["nameDest"].str[0]
```

### Dropped Columns (Data Leakage Prevention)
- `step` (raw time index)
- `datetime` (redundant after feature extraction)
- `isFlaggedFraud` (external flag, not available at prediction time)
- `nameOrig`, `nameDest` (PII, replaced by type indicators)
- `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest` (replaced by debited/credited)

---

## 🧹 Data Preprocessing

### Cleaning Steps
1. **Handle Missing Values**: Drop rows with NaN in critical columns (`isFraud`, `payerdebited`, `recievercredited`)
2. **Handle Infinities**: Replace `inf` and `-inf` with `NaN`, then fill with `0`
3. **Type Conversion**: Ensure categorical columns are strings, target is integer

### Preprocessing Pipeline

```python
# Numeric Features: StandardScaler
numeric_transformer = Pipeline([
    ("scaler", StandardScaler())
])

# Categorical Features: OneHotEncoder
categorical_transformer = Pipeline([
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

# Combined Preprocessor
preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_cols),
    ("cat", categorical_transformer, cat_cols)
])
```

---

## 🤖 Model Training

### Train/Test Split
- **Test Size**: 20%
- **Stratification**: Yes (maintains class distribution)
- **Random State**: 42 (for reproducibility)

### Models Trained

#### 1. **Random Forest** (Baseline Ensemble)
```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=16,
    class_weight="balanced",  # Handles class imbalance
    n_jobs=-1,
    random_state=42
)
```

#### 2. **Logistic Regression** (Baseline Linear)
```python
LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    n_jobs=-1
)
```

#### 3. **XGBoost** (Production Model) ⭐
```python
XGBClassifier(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=<neg/pos ratio>,  # Auto-calculated
    use_label_encoder=False,
    eval_metric="logloss",
    n_jobs=-1,
    random_state=42
)
```

**Why XGBoost?**
- Superior performance on tabular data
- Built-in handling of class imbalance via `scale_pos_weight`
- Robust to overfitting with regularization
- Fast inference for real-time predictions

---

## 📈 Evaluation Metrics

Each model is evaluated on the **test set** using:

### Primary Metrics
1. **ROC-AUC Score**: Measures model's ability to distinguish fraud from legitimate transactions
2. **Precision**: Of transactions flagged as fraud, how many are actually fraud?
3. **Recall**: Of all actual fraud, how many did we catch?
4. **F1-Score**: Harmonic mean of precision and recall

### Classification Report
```python
classification_report(y_test, y_pred, digits=4, output_dict=True)
```

### Confusion Matrix
- True Positives (TP): Correctly identified fraud
- True Negatives (TN): Correctly identified legitimate
- False Positives (FP): Legitimate flagged as fraud
- False Negatives (FN): Fraud missed by model

---

## 💾 Model Persistence

### Saved Artifacts
Each trained model is saved as a **complete pipeline** (preprocessing + classifier):

```python
joblib.dump(pipeline, "xgboost_pipeline.joblib")
```

**Benefits:**
- Single file contains entire transformation + prediction logic
- No need to manually preprocess new data
- Consistent feature engineering at inference time

### Production Model
- **File**: `xgboost_pipeline.joblib`
- **Location**: `backend/ai_models/`
- **Usage**: Loaded by `xgboost_fraud_detector.py` for real-time predictions

---

## 🔮 Inference (Prediction)

### Input Format
```python
sample_tx = {
    "type": "TRANSFER",
    "amount": 250500.00,
    "payerdebited": 250500.00,
    "recievercredited": 0.0,
    "payer_type": "C",
    "reciever_type": "C",
    "hour": 14,
    "day_of_week": 2,
    "date": 13
}
```

### Prediction
```python
df_tx = pd.DataFrame([sample_tx])
fraud_prob = model.predict_proba(df_tx)[0][1]  # Probability of fraud
is_fraud = model.predict(df_tx)[0]  # Binary prediction
```

### Integration
The trained model is integrated into the backend via:
- **File**: `backend/src/utils/xgboost_fraud_detector.py`
- **Function**: `xgboost_fraud_check()`
- **Called by**: `transaction_routes.py` during `preview_send` and `confirm_send`

---

## 🎯 Key Insights from Training

### Feature Importance (XGBoost)
Based on the model's internal feature importance:

| Feature | Importance | Interpretation |
|:--------|:-----------|:---------------|
| **day_of_week** | 65% | **MAJOR SIGNAL**: Unusual transaction days are the strongest fraud indicator |
| **payerdebited** | 13% | Mismatch between stated amount and actual debit is suspicious |
| **amount** | 10% | Raw transaction value matters |
| **date** | 8% | Specific dates (e.g., month-end) influence risk |
| **transaction type** | 2% | TRANSFER vs PAYMENT vs CASH_OUT |

### Class Imbalance Handling
- **Technique**: `scale_pos_weight` (XGBoost) and `class_weight="balanced"` (RF, LR)
- **Effect**: Model learns to prioritize recall (catching fraud) over precision (avoiding false alarms)

### Overfitting Prevention
- **Max Depth**: Limited to 6 (XGBoost) and 16 (RF)
- **Subsampling**: 80% of data per tree (XGBoost)
- **Column Sampling**: 80% of features per tree (XGBoost)

---

## 🚀 Deployment Workflow

1. **Train Model**: Run `fraud_training.py` on historical data
2. **Save Pipeline**: `xgboost_pipeline.joblib` generated
3. **Copy to Backend**: Move `.joblib` file to `backend/ai_models/`
4. **Load in Production**: `xgboost_fraud_detector.py` loads the pipeline
5. **Real-Time Inference**: Called during transaction preview/confirmation

---

## 📝 Reproducibility

### Requirements
```
pandas
numpy
scikit-learn
xgboost
joblib
matplotlib
seaborn
```

### Training Command
```bash
python backend/scripts/fraud_training.py
```

### Random State
All models use `RANDOM_STATE = 42` for deterministic results.

---

## 🔄 Retraining Strategy

### When to Retrain
- New fraud patterns emerge
- Model performance degrades (monitor ROC-AUC)
- Significant changes in transaction behavior

### Best Practices
1. Collect new labeled data (fraud alerts + manual review)
2. Append to `Fraud.csv`
3. Re-run training pipeline
4. Compare new model vs. old model on holdout set
5. Deploy only if performance improves

---

## ⚠️ Limitations

1. **Data Dependency**: Model quality depends on historical fraud labels
2. **Concept Drift**: Fraud tactics evolve; model may become stale
3. **Imbalance**: Even with balancing, rare fraud patterns may be missed
4. **Feature Availability**: Requires all 9 features at prediction time

---

## 📚 References

- **XGBoost Documentation**: https://xgboost.readthedocs.io/
- **Scikit-learn Pipelines**: https://scikit-learn.org/stable/modules/compose.html
- **Fraud Detection Best Practices**: Industry-standard imbalanced classification techniques

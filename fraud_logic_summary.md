# Fraud Detection & Biometric Bypass Summary

This document outlines the logic used by TrustWallet to detect suspicious activity, when a transaction proceeds smoothly, and how users can bypass security blocks.

---

## 🛑 When Fraud is Detected

The system uses a two-layered defense: **Heuristic Rules** and **XGBoost Machine Learning**.

### 1. Heuristic Rules (Rule-Based)
| Rule | Severity | Trigger | Result |
| :--- | :--- | :--- | :--- |
| **Max Limit Exceeded** | High | Amount > 100,000 BDT | **BLOCK** |
| **Historical Spike** | High | Amount > 2x your historical max | **BLOCK** |
| **Velocity Spike** | Medium-High | 3+ transfers in 5 mins (value > 500 BDT) | **BLOCK** |
| **Testing Pattern** | Medium-High | Small transfers followed by a large one | **BLOCK** |
| **New High-Value Receiver**| Medium | First time sending to someone (amt > 25,000) | **BLOCK** |
| **Average Spike** | Medium | Amount > 1.5x your average | **BLOCK** |
| **Off-Hours / Weekend** | Low | Late-night high-value transactions | **WARNING ONLY** |

### 2. Machine Learning (XGBoost)
The system uses a high-performance XGBoost model trained on historical fraud patterns. It analyzes **9 key parameters** for every transaction:

| Parameter | Description | Why it matters? |
| :--- | :--- | :--- |
| **Amount** | Total BDT being sent | Large unusual amounts are high risk. |
| **Hour** | Time of day (0-23) | Night-time (2 AM - 4 AM) is higher risk. |
| **Day of Week** | Mon-Sun (0-6) | Weekend anomalies are flagged. |
| **Date** | Day of month (1-31) | Payday or end-of-month spikes. |
| **Payer Debited** | Amount from your wallet | Corresponds to your spending ability. |
| **Receiver Credited** | Amount to the recipient | Matches if it's a standard transfer. |
| **Transaction Type** | e.g. "TRANSFER" | Different types have different risk levels. |
| **Payer Type** | "C" (Customer) | Identifies your account behavior. |
| **Receiver Type** | "C" or "M" (Merchant) | Sending to a merchant is lower risk than P2P. |

#### Risk Levels (Probability)
The model outputs a **Fraud Probability** (0.0 to 1.0). The app translates this for you:
- **Low Risk (< 0.3)**: No prompts. Smooth transaction.
- **Medium Risk (0.3 - 0.7)**: Shows a warning. May require biometrics.
- **High Risk (> 0.7)**: **BLOCKS** the transaction and **REQUIRES** Face ID to proceed.

---

## 📈 Model Bias & Feature Importance

Through technical analysis, we've identified exactly which features "drive" the machine learning decisions. This tells us what the model is most "biased" towards when looking for fraud.

### Top 5 Most Influential Features:
| Feature | Importance Score | What it means? |
| :--- | :--- | :--- |
| **Day of Week** | **0.65 (65%)** | **MAJOR BIAS**: The model relies heavily on which day you are sending money. Transactions on "unusual" days for your profile are the #1 trigger for blocks. |
| **Payer Debited** | 0.13 (13%) | The system checks if the amount leaving your wallet fits your spending pattern. |
| **Amount** | 0.10 (10%) | The raw BDT value. High amounts naturally carry weight. |
| **Date** | 0.08 (8%) | Specific dates (like month-end) influence the risk calculation. |
| **Transaction Type** | 0.02 (2%) | "TRANSFER" vs "CASH_OUT" provides the context for the behavior. |

> [!NOTE]
> **Why is Day of Week so high?**
> A score of 0.65 is very high. This means if you suddenly send a large amount on a day you usually don't use the app (e.g., a Sunday if you only use it on weekdays), the system will almost certainly ask for Face ID.

---

## 🔓 How to Bypass a Block

Most fraud blocks can be overridden with biometrics, but **Critical** cases are kept as a "Hard Stop" for security.

### 1. Bypassable Cases (The 5-Minute Master Key)
If you trigger any of these, a single Face Scan grants a **5-minute bypass**:
- **ML Flags**: Any machine learning detection.
- **High Amount Spike**: Sending 2x your historical maximum.
- **Velocity Spike**: 3+ transfers in 5 minutes (for values > 500 BDT).
- **New Receiver**: Large transfer to a first-time recipient.
- **Testing Pattern**: Small transfer followed by a larger one.

### 2. Unbypassable Cases (The Hard Stop)
The following requires **Manual Review** and CANNOT be bypassed with a face scan:
- **Critical Velocity**: Sending multiple high-value transactions (≥50,000 BDT) in a very short time window. 
  - *Reason: This prevents a thief from rapidly draining your wallet even if they get one successful scan.*

### 3. Automatic Account Cleanup
- Successfully scanning your face **immediately resolves** all pending "Unresolved" fraud alerts on your account.
- This lowers your account risk score instantly, preventing a "sticky" block.

### 4. Smart UI Guidance
- If `face_enrolled == false`: User is prompted to **"Setup Face ID"** (Enrollment).
- If `face_enrolled == true`: User is prompted to **"Verify Face"**.
- After setup or verification, the original transaction is unblocked and allowed to proceed.

## 🔍 How Face Verification Works

TrustWallet uses industry-standard AI to ensure that the person making a transaction is the rightful owner of the account.

### 1. Secure Enrollment
- When you first set up Face ID, your image is securely uploaded to **Supabase Storage**.
- The backend stores a specific pointer to this image in your profile so it can be retrieved for comparison.

### 2. AI-Powered Comparison
The system uses a two-stage process to verify it's really you:

#### Stage A: Face Detection
- **Detection Check**: The system first scans the image to ensure a human face is clearly visible. 
- **Auto-Alignment**: If you are tilted or not looking straight, the AI "straightens" the face internally to get a better look.
- **Security Check**: This stage also ensures no "empty" or "non-face" images are used to trick the system.

#### Stage B: Deep Matching (Facenet512)
- **Embedding Creation**: The AI converts your face into a list of **512 unique numbers** (an embedding). These numbers represent your unique facial features (distance between eyes, nose shape, etc.).
- **Mathematical Distance**: The system compares your *new* 512 numbers with your *enrolled* 512 numbers.
- **Threshold**: It calculates a "Cosine Distance." If the distance is very small (near 0), it means the faces are a perfect match. If the distance is large, it rejects the verification.

### 3. Immediate Impact of Success
When a scan is successful, the system performs three critical tasks in one go:
1. **Unblocks Pending Alerts**: It immediately finds every "Unresolved" fraud alert on your account and marks them as "Resolved."
2. **Lowers Risk Score**: By resolving these alerts, your account's health score returns to normal.
3. **Starts the Bypass Window**: It marks your account as "Verified" for the next **5 minutes**, allowing you to bypass any further fraud triggers during that time.

---

## ✅ Smooth Transactions (No Prompts)

Transactions proceed without any "Face Verify" or "Setup" prompts in these cases:

1.  **Low Risk**: The transaction doesn't trigger any rules or ML flags.
2.  **Small Amounts**: Transfers under 500 BDT are exempt from the "Rapid Velocity" rule.
3.  **Low Severity**: If a rule is flagged as "Low" severity (e.g., late-night shopping), it only shows a warning banner but does NOT block the transfer.
4.  **Existing Trust**: Sending to a known receiver with a typical amount.

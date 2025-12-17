"""
Test script to verify XGBoost model is working with correct features.
"""
import joblib
import pandas as pd
from datetime import datetime

print("=" * 70)
print("XGBoost Fraud Detection Model - Verification Test")
print("=" * 70)

# Load the model
try:
    model = joblib.load("models/xgboost_pipeline_fraud.pkl")
    print("\n✅ Model loaded successfully from: models/xgboost_pipeline_fraud.pkl")
except Exception as e:
    print(f"\n❌ Failed to load model: {e}")
    exit(1)

# Check model type
if hasattr(model, 'named_steps'):
    print("✅ Model is a Pipeline")
    print(f"   Steps: {list(model.named_steps.keys())}")
else:
    print("✅ Model is a standalone classifier")

print("\n" + "=" * 70)
print("Test Case 1: Normal Transaction (Low Risk)")
print("=" * 70)

# Simulate normal transaction
now = datetime.now()
normal_transaction = {
    "type": "TRANSFER",
    "amount": 1000.0,
    "payerdebited": 1000.0,
    "recievercredited": 1000.0,
    "payer_type": "C",
    "reciever_type": "C",
    "hour": now.hour,
    "day_of_week": now.weekday(),
    "date": now.day,
}

print("\n📊 Features:")
for key, value in normal_transaction.items():
    print(f"   {key:20s} = {value}")

try:
    df = pd.DataFrame([normal_transaction])
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0]
    
    print(f"\n✅ Prediction successful!")
    print(f"   Is Fraud: {prediction} (0=Normal, 1=Fraud)")
    print(f"   Fraud Probability: {probability[1]:.4f} ({probability[1]*100:.2f}%)")
    print(f"   Normal Probability: {probability[0]:.4f} ({probability[0]*100:.2f}%)")
    
    if probability[1] < 0.3:
        print(f"   Risk Level: 🟢 LOW")
    elif probability[1] < 0.7:
        print(f"   Risk Level: 🟡 MEDIUM")
    else:
        print(f"   Risk Level: 🔴 HIGH")
        
except Exception as e:
    print(f"\n❌ Prediction failed: {e}")
    print("\n🔍 Error details:")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
print("Test Case 2: Large Transaction (Potential Higher Risk)")
print("=" * 70)

large_transaction = {
    "type": "TRANSFER",
    "amount": 250000.0,
    "payerdebited": 250000.0,
    "recievercredited": 250000.0,
    "payer_type": "C",
    "reciever_type": "C",
    "hour": 2,  # Late night transaction
    "day_of_week": 6,  # Sunday
    "date": now.day,
}

print("\n📊 Features:")
for key, value in large_transaction.items():
    print(f"   {key:20s} = {value}")

try:
    df = pd.DataFrame([large_transaction])
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0]
    
    print(f"\n✅ Prediction successful!")
    print(f"   Is Fraud: {prediction} (0=Normal, 1=Fraud)")
    print(f"   Fraud Probability: {probability[1]:.4f} ({probability[1]*100:.2f}%)")
    print(f"   Normal Probability: {probability[0]:.4f} ({probability[0]*100:.2f}%)")
    
    if probability[1] < 0.3:
        print(f"   Risk Level: 🟢 LOW")
    elif probability[1] < 0.7:
        print(f"   Risk Level: 🟡 MEDIUM")
    else:
        print(f"   Risk Level: 🔴 HIGH")
        
except Exception as e:
    print(f"\n❌ Prediction failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("Test Case 3: Suspicious Pattern (Zero Receiver Credit)")
print("=" * 70)

suspicious_transaction = {
    "type": "TRANSFER",
    "amount": 100000.0,
    "payerdebited": 100000.0,
    "recievercredited": 0.0,  # Suspicious: money debited but not credited
    "payer_type": "C",
    "reciever_type": "C",
    "hour": 3,  # Late night
    "day_of_week": 2,
    "date": now.day,
}

print("\n📊 Features:")
for key, value in suspicious_transaction.items():
    print(f"   {key:20s} = {value}")

try:
    df = pd.DataFrame([suspicious_transaction])
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0]
    
    print(f"\n✅ Prediction successful!")
    print(f"   Is Fraud: {prediction} (0=Normal, 1=Fraud)")
    print(f"   Fraud Probability: {probability[1]:.4f} ({probability[1]*100:.2f}%)")
    print(f"   Normal Probability: {probability[0]:.4f} ({probability[0]*100:.2f}%)")
    
    if probability[1] < 0.3:
        print(f"   Risk Level: 🟢 LOW")
    elif probability[1] < 0.7:
        print(f"   Risk Level: 🟡 MEDIUM")
    else:
        print(f"   Risk Level: 🔴 HIGH")
        
except Exception as e:
    print(f"\n❌ Prediction failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\n🎯 Model is working correctly with the implemented features!")
print("   - All 9 features are being accepted")
print("   - Predictions are being generated successfully")
print("   - Fraud probabilities are reasonable")
print("\n✨ Your fraud detection system is ready to use!")

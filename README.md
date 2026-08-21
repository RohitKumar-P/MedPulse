# MedPulse Health AI

MedPulse is an AI-assisted health screening platform that combines:

- Machine Learning
- Explainable AI
- SHAP
- Retrieval-Augmented Generation (RAG)
- Local AI through Ollama
- FastAPI backend
- Database services
- Modern frontend

## Important

MedPulse is a health screening and information system.

It does NOT provide a confirmed medical diagnosis.

The ML model performs the prediction. The AI explains and verifies the result using the available information and retrieved evidence.

---

## How MedPulse Works

User
  |
  v
Health Survey
  |
  v
Input Validation
  |
  v
Machine Learning Prediction
  |
  +----> SHAP Explanation
  |
  v
RAG Evidence Retrieval
  |
  v
AI Verification
  |
  v
Patient-Friendly Result

---

## Core Architecture

ML:
Prediction and risk estimation.

SHAP:
Explains which model features influenced the prediction.

RAG:
Retrieves relevant supporting information.

AI:
Explains the ML result in simple language and checks that the explanation does not invent information.

Database:
Stores application data required by the platform.

Frontend:
Provides the user interface.

Backend:
Connects the frontend, ML models, RAG, AI and database.

---

## User Screening

The screening system should ask only information that is relevant to the selected screening.

Required information should be mandatory when the selected model genuinely needs it.

Optional information may be skipped.

If optional information is skipped, MedPulse should warn the user:

"Some information is missing. You can continue, but providing the requested details may improve the quality of the screening."

If essential information is missing, the user should be asked to provide it before the prediction can run.

If additional information is needed, the screening system should ask follow-up questions.

Questions should use normal language rather than complicated medical terminology.

Example:

Instead of:

"Do you experience polyuria?"

Ask:

"Are you urinating more often than usual?"

Instead of:

"Do you experience polydipsia?"

Ask:

"Are you unusually thirsty?"

---

## ML Prediction

The machine learning system performs the primary prediction.

The AI must not simply guess a disease from the user's text.

The ML system produces the screening prediction.

Example output:

- Condition
- Probability
- Risk score
- Risk level
- Contributing factors
- Patient-specific factors

The result is a screening estimate and not a confirmed diagnosis.

---

## Current Diabetes Model

The current diabetes model uses:

- pregnancies
- glucose
- blood_pressure
- skin_thickness
- insulin
- bmi
- diabetes_pedigree
- age

The model uses an ExtraTreesClassifier.

Current configuration includes:

- 600 estimators
- max_depth = 8
- min_samples_leaf = 3
- class_weight = balanced
- random_state = 42
- probability calibration

The model is stored using Joblib.

Model directory:

backend/ml/models/

---

## Explainable AI

MedPulse uses SHAP to explain individual predictions.

Example:

Feature:
glucose

Value:
120

Direction:
decreases risk

The explanation must describe what the model did.

It must not claim that a feature proves that a person has or does not have a disease.

---

## RAG

The RAG system retrieves relevant evidence before the local AI generates an explanation.

Pipeline:

ML prediction
      |
      v
Evidence retrieval
      |
      v
Medical evidence
      |
      v
AI verification
      |
      v
Final explanation

The AI should use retrieved evidence when available.

If evidence is insufficient, the AI should explicitly state that additional information may be required.

---

## AI Verification

The AI verification layer receives:

- ML prediction
- Probability
- Risk level
- Model factors
- Patient information
- Retrieved evidence

The AI is instructed to:

1. Preserve the ML prediction.
2. Never invent medical information.
3. Never invent symptoms.
4. Never invent test results.
5. Never invent medications.
6. Never invent medical history.
7. Use supplied evidence.
8. Explain medical concepts simply.
9. Identify missing information.
10. Recommend sensible next steps.
11. State that the result is not a confirmed diagnosis.

---

## AI Safety

The AI must NOT:

- Claim certainty.
- Confirm that a person definitely has a disease.
- Invent symptoms.
- Invent laboratory results.
- Invent medical history.
- Invent medications.
- Recommend prescription medicines.
- Recommend medication dosages.
- Pretend missing information exists.
- Override the ML prediction without an explicit application rule.

The AI SHOULD:

- Explain the screening result.
- Explain important contributing factors.
- Explain uncertainty.
- Identify missing information.
- Ask for relevant additional information.
- Use simple language.
- Recommend appropriate professional evaluation when necessary.

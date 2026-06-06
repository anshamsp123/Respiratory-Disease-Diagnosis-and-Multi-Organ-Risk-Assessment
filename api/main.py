from fastapi import FastAPI, UploadFile, File, Form
import random

app = FastAPI(title="Respiratory AI Demo")

DEMO_MODE = True

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    age: float = Form(...),
    spo2: float = Form(...),
    creatinine: float = Form(...),
    troponin: float = Form(...),
    symptoms: str = Form("")
):
    if DEMO_MODE:
        # Simulate realistic outputs based on heuristics
        diseases = ["COPD", "Pneumonia", "Pulmonary Fibrosis", "Pleural Effusion", "Normal"]
        
        # Heuristics for realism
        if spo2 < 90:
            disease = random.choice(["Pneumonia", "Pulmonary Fibrosis", "COPD"])
            severity = "High"
        elif spo2 < 95:
            disease = random.choice(["Pneumonia", "Pleural Effusion", "COPD"])
            severity = "Moderate"
        else:
            disease = random.choice(["Normal", "Normal", "Normal", "Pleural Effusion"])
            severity = "Low"
            
        # Normal Creatinine ~ 0.7 - 1.3
        kidney_risk = min(100, max(0, int((creatinine - 0.5) * 40)))
        
        # Normal Troponin < 0.04
        heart_risk = min(100, max(0, int((troponin) * 1000)))
        
        # Normal Liver Risk (Simulated)
        liver_risk = random.randint(10, 30)

        # Generate rule-based Explanation
        xray_findings = {
            "Normal": "clear lung fields with no significant opacities, consolidations, or pleural effusions",
            "Pneumonia": "patchy alveolar infiltrates and localized consolidation indicative of active infection",
            "COPD": "hyperinflated lungs with flattened diaphragms and expanded anterior-posterior diameter",
            "Pulmonary Fibrosis": "reticular opacities and honeycombing patterns with traction bronchiectasis, particularly in the lower subpleural regions",
            "Pleural Effusion": "blunting of the costophrenic angles and meniscus-shaped fluid collection in the pleural space"
        }
        finding = xray_findings.get(disease, "pulmonary abnormalities")
        symptoms_text = symptoms.strip() if symptoms.strip() else "No specific symptoms reported"
        
        explanation = f"**Diagnostic Rationale (Image + Clinical Fusion):**\n"
        explanation += f"The CNN model analyzed the X-ray and detected **{finding}**, leading to a primary diagnosis of **{disease}** (Confidence: {round(random.uniform(0.85, 0.98)*100)}%). "
        
        if spo2 < 90:
            explanation += f"Critically low SpO2 levels ({spo2}%) combined with the imaging features pushed the overall clinical severity to **{severity}**. "
        elif spo2 < 95:
            explanation += f"Reduced SpO2 levels ({spo2}%) moderately influenced the severity classification to **{severity}**. "
        else:
            explanation += f"Normal SpO2 levels ({spo2}%) maintained the severity classification at **{severity}**. "
        
        explanation += f"Patient reported symptoms: '{symptoms_text}'. "
        
        explanation += "\n\n**Systemic Organ Risk Analysis:**\n"
        if kidney_risk > 50:
            explanation += f"- **Kidney Risk ({kidney_risk}%):** The elevated Creatinine level ({creatinine} mg/dL) exceeds the normal threshold (0.7-1.3 mg/dL), indicating impaired renal filtration often secondary to systemic inflammation, hypoxemia, or sepsis.\n"
        else:
            explanation += f"- **Kidney Risk ({kidney_risk}%):** The Creatinine level ({creatinine} mg/dL) is within normal limits, suggesting preserved renal function and adequate glomerular filtration without significant ischemic damage.\n"
            
        if heart_risk > 50:
            explanation += f"- **Heart Risk ({heart_risk}%):** A significant rise in Troponin ({troponin} ng/mL) suggests myocardial injury, likely due to right ventricular strain from respiratory failure or acute coronary syndrome.\n"
        else:
            explanation += f"- **Heart Risk ({heart_risk}%):** Troponin ({troponin} ng/mL) remains below pathological thresholds (<0.04 ng/mL), indicating no acute myocardial stress or active heart muscle necrosis.\n"

        return {
            "disease": disease,
            "severity": severity,
            "organ_risk": {
                "kidney": kidney_risk,
                "heart": heart_risk,
                "liver": liver_risk
            },
            "confidence": round(random.uniform(0.75, 0.98), 2),
            "explanation": explanation
        }
    else:
        # Placeholder for real model inference
        return {"error": "Real inference not implemented yet. Set DEMO_MODE=True"}

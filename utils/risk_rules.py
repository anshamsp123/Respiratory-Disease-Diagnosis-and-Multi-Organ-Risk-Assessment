def generate_alerts(spo2, creatinine, troponin):
    alerts = []
    if spo2 < 90:
        alerts.append({"level": "critical", "msg": f"Hypoxia Risk: SpO2 is critically low ({spo2}%)"})
    elif spo2 < 95:
        alerts.append({"level": "warning", "msg": f"Low Oxygen: SpO2 is below optimal ({spo2}%)"})
        
    if creatinine > 1.3:
        alerts.append({"level": "warning", "msg": f"Kidney Stress: Elevated Creatinine ({creatinine} mg/dL)"})
        
    if troponin > 0.04:
        alerts.append({"level": "critical", "msg": f"Cardiac Risk: Elevated Troponin ({troponin} ng/mL)"})
        
    return alerts

def get_clinical_correlations(spo2, creatinine, troponin):
    correlations = []
    if troponin > 0.04:
        correlations.append(f"**High Troponin ({troponin} ng/mL)** → Cardiac stress or potential myocardial injury.")
    if spo2 < 90:
        correlations.append(f"**Low SpO2 ({spo2}%)** → High respiratory severity and hypoxia risk.")
    elif spo2 < 95:
        correlations.append(f"**Reduced SpO2 ({spo2}%)** → Moderate respiratory impairment.")
    if creatinine > 1.3:
        correlations.append(f"**Elevated Creatinine ({creatinine} mg/dL)** → Kidney stress, reduced renal filtration.")
        
    if not correlations:
        correlations.append("Biomarkers are within normal ranges, indicating stable systemic organ function.")
    return correlations

def get_treatment_suggestions(spo2, severity):
    suggestions = [
        "Monitor vital signs and oxygen levels regularly.",
        "Follow up with repeat imaging if symptoms persist or worsen.",
        "Repeat comprehensive biomarker tests in 24-48 hours."
    ]
    if spo2 < 90:
        suggestions.insert(0, "Consider immediate supplemental oxygen therapy.")
    if severity == "High":
        suggestions.insert(0, "Immediate clinical evaluation and potential admission recommended.")
    return suggestions

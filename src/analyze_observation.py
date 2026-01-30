def analyze_blood_pressure(systolic, diastolic):
    """
    Analyse une mesure de pression artérielle
    et retourne le type d'anomalie détectée
    selon les recommandations médicales.
    """

    if systolic is None or diastolic is None:
        return ["invalid_measurement"]


    # Hypertensive crisis (urgence)
    if systolic > 180 or diastolic > 120:
        return ["hypertensive_crisis"]

    # Hypertension Stage 2
    if systolic >= 140 or diastolic >= 90:
        return ["hypertension_stage_2"]

    # Hypertension Stage 1
    if 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return ["hypertension_stage_1"]

    # Elevated blood pressure
    if 120 <= systolic <= 129 and diastolic < 80:
        return ["elevated"]


def extract_bp_from_fhir_observation(observation: dict):
    """
    Extrait systolic et diastolic d'une Observation FHIR.
    On cherche les composants par leur code LOINC:
    - 8480-6 = systolic
    - 8462-4 = diastolic
    """

    systolic = None
    diastolic = None

    for comp in observation.get("component", []):
        coding_list = comp.get("code", {}).get("coding", [])
        if not coding_list:
            continue

        code = coding_list[0].get("code")
        value = comp.get("valueQuantity", {}).get("value")

        if code == "8480-6":
            systolic = value
        elif code == "8462-4":
            diastolic = value

    return systolic, diastolic


if __name__ == "__main__":
    # Exemple minimal inspiré de ton générateur
    observation = {
        "resourceType": "Observation",
        "subject": {"reference": "Patient/PAT-9486"},
        "effectiveDateTime": "2026-01-16T15:42:56.834661Z",
        "component": [
            {
                "code": {"coding": [{"code": "8480-6"}]},
                "valueQuantity": {"value": 140.0, "unit": "mmHg"},
            },
            {
                "code": {"coding": [{"code": "8462-4"}]},
                "valueQuantity": {"value": 54.0, "unit": "mmHg"},
            },
        ],
    }

    systolic, diastolic = extract_bp_from_fhir_observation(observation)
    print("Systolic:", systolic, "Diastolic:", diastolic)

    anomalies = analyze_blood_pressure(systolic, diastolic)

    if anomalies:
        print("Anomalie détectée :", anomalies)
    else:
        print("Pression normale")

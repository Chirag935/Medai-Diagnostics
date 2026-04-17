"""
Demo values for all diseases - realistic clinical parameters
"""

DIABETES_DEMO = {
    "pregnancies": 2,
    "glucose": 130,
    "blood_pressure": 80,
    "skin_thickness": 25,
    "insulin": 120,
    "bmi": 28.5,
    "diabetes_pedigree": 0.6,
    "age": 45
}

HEART_DISEASE_DEMO = {
    "age": 55,
    "sex": 1,
    "cp": 2,
    "trestbps": 140,
    "chol": 240,
    "fbs": 0,
    "restecg": 1,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 1.5,
    "slope": 1,
    "ca": 0,
    "thal": 2
}

LIVER_DISEASE_DEMO = {
    "age": 35,
    "gender": 1,
    "total_bilirubin": 1.2,
    "direct_bilirubin": 0.3,
    "alkaline_phosphotase": 200,
    "alamine_aminotransferase": 35,
    "aspartate_aminotransferase": 40,
    "total_proteins": 7.2,
    "albumin": 4.0,
    "albumin_globulin_ratio": 1.2
}

KIDNEY_DISEASE_DEMO = {
    "age": 50,
    "blood_pressure": 80,
    "specific_gravity": 1.020,
    "albumin": 1,
    "sugar": 0,
    "red_blood_cells": 1,
    "pus_cell": 0,
    "pus_cell_clumps": 0,
    "bacteria": 0,
    "blood_glucose_random": 140,
    "blood_urea": 40,
    "serum_creatinine": 1.2,
    "sodium": 135,
    "potassium": 4.5,
    "hemoglobin": 13.5,
    "packed_cell_volume": 40,
    "white_blood_cell_count": 8000,
    "red_blood_cell_count": 4.5,
    "hypertension": 0,
    "diabetes_mellitus": 0,
    "coronary_artery_disease": 0,
    "appetite": 0,
    "pedal_edema": 0,
    "anemia": 0
}

BREAST_CANCER_DEMO = {
    "radius_mean": 17.0,
    "texture_mean": 20.0,
    "perimeter_mean": 110.0,
    "area_mean": 900.0,
    "smoothness_mean": 0.1,
    "compactness_mean": 0.15,
    "concavity_mean": 0.12,
    "concave_points_mean": 0.08,
    "symmetry_mean": 0.18,
    "fractal_dimension_mean": 0.06
}

ALZHEIMER_DEMO = {
    "age": 75,
    "gender": 1,
    "education": 12,
    "ses": 2,
    "mmse": 22,
    "cdr": 0.5,
    "etiv": 1500,
    "nwbv": 0.70,
    "asf": 1.2
}

DEMO_VALUES = {
    "diabetes": DIABETES_DEMO,
    "heart_disease": HEART_DISEASE_DEMO,
    "liver_disease": LIVER_DISEASE_DEMO,
    "kidney_disease": KIDNEY_DISEASE_DEMO,
    "breast_cancer": BREAST_CANCER_DEMO,
    "alzheimer": ALZHEIMER_DEMO
}

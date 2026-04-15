# MedAI Diagnostics - Datasets Guide

Complete guide to all datasets used for each disease prediction module.

## 📊 Dataset Summary

| Disease | Dataset Name | Type | Samples | Features/Format |
|---------|-------------|------|---------|-----------------|
| **Diabetes** | PIMA Indians Diabetes | CSV | 768 | 8 clinical features |
| **Breast Cancer** | Wisconsin Diagnostic | CSV | 569 | 30 numeric features |
| **Heart Disease** | UCI Cleveland | CSV | 303 | 13 clinical features |
| **Liver Disease** | Indian Liver Patient | CSV | 583 | 10 features |
| **Kidney Disease** | CKD Dataset | CSV | 400 | 24 features + 11 labs |
| **Alzheimer's** | OASIS + Synthetic | CSV | 500+ | 8 clinical features |
| **Pneumonia** | Synthetic X-rays | Images | 2000 | 224x224 grayscale |
| **Malaria** | Synthetic Blood Smears | Images | 2000 | 224x224 RGB |

---

## 🔬 Detailed Dataset Information

### 1. Diabetes Prediction
**Dataset:** PIMA Indians Diabetes Database (UCI ML Repository)

**Input Features:**
| Feature | Description | Range | Unit |
|---------|-------------|-------|------|
| `pregnancies` | Number of times pregnant | 0-17 | count |
| `glucose` | Plasma glucose concentration | 0-199 | mg/dL |
| `blood_pressure` | Diastolic blood pressure | 0-122 | mm Hg |
| `skin_thickness` | Triceps skin fold thickness | 0-99 | mm |
| `insulin` | 2-Hour serum insulin | 0-846 | μU/mL |
| `bmi` | Body mass index | 0-67.1 | kg/m² |
| `diabetes_pedigree` | Diabetes pedigree function | 0.078-2.42 | - |
| `age` | Age in years | 21-81 | years |

**Output:** Binary (0 = No Diabetes, 1 = Diabetes)

---

### 2. Breast Cancer Prediction
**Dataset:** Wisconsin Diagnostic Breast Cancer (WDBC)

**Input Features (30 total):**
- 10 features × 3 statistics (mean, standard error, worst)
- radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, fractal dimension

**Output:** Binary (M = Malignant, B = Benign)

---

### 3. Heart Disease Prediction
**Dataset:** UCI Cleveland Heart Disease Dataset

**Input Features:**
| Feature | Description | Values/Range |
|---------|-------------|--------------|
| `age` | Age in years | 29-77 |
| `sex` | Gender | 1 = Male, 0 = Female |
| `cp` | Chest pain type | 0-3 |
| `trestbps` | Resting blood pressure | 94-200 mm Hg |
| `chol` | Serum cholesterol | 126-564 mg/dl |
| `fbs` | Fasting blood sugar > 120 | 1 = True, 0 = False |
| `restecg` | Resting ECG results | 0-2 |
| `thalach` | Max heart rate achieved | 71-202 |
| `exang` | Exercise induced angina | 1 = Yes, 0 = No |
| `oldpeak` | ST depression by exercise | 0-6.2 |
| `slope` | Slope of peak exercise ST | 0-2 |
| `ca` | Number of major vessels | 0-3 |
| `thal` | Thalassemia | 3 = Normal, 6 = Fixed, 7 = Reversible |

---

### 4. Liver Disease Prediction
**Dataset:** Indian Liver Patient Dataset (ILPD)

**Input Features:**
| Feature | Description | Range |
|---------|-------------|-------|
| `age` | Patient age | 4-90 years |
| `gender` | Gender | 1 = Male, 0 = Female |
| `total_bilirubin` | Total bilirubin | 0.4-75.0 mg/dL |
| `direct_bilirubin` | Direct bilirubin | 0.1-19.7 mg/dL |
| `alkaline_phosphatase` | ALP enzyme | 63-2110 U/L |
| `alamine_aminotransferase` | ALT (SGPT) | 10-2000 U/L |
| `aspartate_aminotransferase` | AST (SGOT) | 10-4929 U/L |
| `total_proteins` | Total proteins | 2.7-9.6 g/dL |
| `albumin` | Albumin | 0.9-5.5 g/dL |
| `albumin_globulin_ratio` | A/G ratio | 0.3-2.8 |

---

### 5. Kidney Disease (CKD) Prediction
**Input Features:**
| Category | Features |
|----------|----------|
| Clinical | age, blood_pressure, specific_gravity, albumin, sugar |
| Cell Morphology | red_blood_cells, pus_cell, pus_cell_clumps, bacteria |
| Lab Values | blood_glucose, blood_urea, serum_creatinine, sodium, potassium, hemoglobin |
| Counts | packed_cell_volume, white_blood_cell_count, red_blood_cell_count |
| Conditions | hypertension, diabetes_mellitus, coronary_artery_disease, appetite, pedema, anemia |

---

### 6. Alzheimer's Detection
**Input Features:**
| Feature | Description | Range |
|---------|-------------|-------|
| `age` | Patient age | 60-100 |
| `gender` | Gender | 1 = Male, 0 = Female |
| `education_years` | Years of education | 0-20 |
| `mmse_score` | Mini-Mental State Exam | 0-30 |
| `memory_complaints` | Memory issues | 0-5 scale |
| `behavioral_problems` | Behavioral symptoms | 0-5 scale |
| `adl_score` | Daily living activities | 0-10 |
| `forgetfulness` | Forgetfulness frequency | 0-5 scale |

---

### 7. Pneumonia Detection
**Dataset:** Chest X-ray Images

**Image Format:**
- Resolution: 224×224 pixels
- Mode: Grayscale
- Format: PNG/JPG

**Normal X-ray Features:**
- Clear lung fields
- Proper aeration
- Visible rib patterns
- Heart shadow normal

**Pneumonia X-ray Features:**
- Consolidations (white patches)
- Infiltrates
- Lower lobe predominance
- Increased opacity

**Pattern Types:**
1. **Lobar Consolidation** - Large dense area in one lobe
2. **Patchy Infiltrates** - Scattered white spots
3. **Interstitial Pattern** - Network of fine lines

---

### 8. Malaria Detection
**Dataset:** Blood Smear Images

**Image Format:**
- Resolution: 224×224 pixels
- Mode: RGB
- Format: PNG/JPG

**Normal Cell Features:**
- Uniform red blood cells
- No dark spots
- Smooth edges
- Consistent color

**Infected Cell Features:**
- Dark spots/ring forms
- Irregular shapes
- Parasite presence
- Color variations

---

## 📥 How to Use Your Own Data

### For Clinical Data (CSV):
1. Create CSV with matching column names
2. Place in `backend/data/` directory
3. Run training script

### For Medical Images:
1. Organize in folders:
   ```
   data/
   ├── pneumonia/
   │   ├── normal/
   │   └── pneumonia/
   └── malaria/
       ├── uninfected/
       └── parasitized/
   ```
2. Retrain CNN models

---

## 🔗 Dataset Sources

| Dataset | Source URL |
|---------|-----------|
| PIMA Diabetes | https://archive.ics.uci.edu/ml/datasets/diabetes |
| WDBC | https://archive.ics.uci.edu/ml/datasets/Breast+Cancer+Wisconsin+(Diagnostic) |
| Heart Disease | https://archive.ics.uci.edu/ml/datasets/heart+disease |
| Liver Disease | https://archive.ics.uci.edu/ml/datasets/ILPD |
| Kidney Disease | https://archive.ics.uci.edu/ml/datasets/Chronic_Kidney_Disease |
| Chest X-rays | https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia |
| Malaria Cells | https://www.kaggle.com/datasets/iarunava/cell-images-for-detecting-malaria |

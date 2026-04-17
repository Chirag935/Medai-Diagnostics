# MedAI Diagnostics

AI-powered medical diagnostics platform with 8 disease prediction models.

## Tech Stack
- **Frontend**: Next.js 14, TypeScript, TailwindCSS
- **Backend**: FastAPI, scikit-learn, Python 3.11
- **Models**: 6 tabular + 2 image-based ML models

## Disease Modules
| Disease | Type | Input |
|---------|------|-------|
| Diabetes | Tabular | 8 clinical parameters |
| Heart Disease | Tabular | 13 parameters |
| Breast Cancer | Tabular | 30 parameters |
| Kidney Disease | Tabular | 24 parameters |
| Liver Disease | Tabular | 10 parameters |
| Alzheimer's | Tabular | 12 parameters |
| Pneumonia | Image | Chest X-ray |
| Malaria | Image | Blood smear |

## Local Development
```bash
.\start.bat
```

## Deployment
- **Frontend**: Vercel (set `NEXT_PUBLIC_API_URL` env var)
- **Backend**: Render (Python, uses `Procfile`)

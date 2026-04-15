# MedAI Diagnostics - Medical AI Disease Detection Platform

A comprehensive full-stack medical AI web application for disease detection and prediction powered by machine learning.

## Overview

MedAI Diagnostics is a professional medical-grade platform that serves as both a technical demonstration and educational tool for AI in healthcare. The platform features 8 disease detection modules with real-time predictions, confidence scoring, and comprehensive performance metrics.

## Features

### Disease Detection Modules
1. **Pneumonia Detection** - Chest X-ray analysis with CNN and Grad-CAM visualization
2. **Malaria Detection** - Blood smear image analysis for parasite detection
3. **Breast Cancer Prediction** - Clinical feature analysis for malignancy detection
4. **Diabetes Prediction** - Risk assessment based on clinical parameters
5. **Alzheimer's Detection** - MRI brain scan analysis for cognitive impairment
6. **Liver Disease Prediction** - Biochemical marker analysis for liver function
7. **Kidney Disease (CKD)** - Comprehensive clinical attribute assessment
8. **Heart Disease Prediction** - Cardiovascular risk factor analysis

### Platform Features
- Real-time confidence scoring (0-100%)
- Risk classification badges (LOW/MODERATE/HIGH/CRITICAL)
- Clinical explanations for predictions
- Model performance dashboard with comprehensive metrics
- Demo Mode and Presentation Mode
- PDF report generation
- Responsive design with medical-grade UI

## Technical Architecture

### Frontend
- **Framework**: Next.js 14+ with TypeScript
- **Styling**: TailwindCSS with custom medical theme
- **UI Components**: shadcn/ui components
- **Charts**: Recharts for data visualization
- **State Management**: Zustand
- **File Upload**: React Dropzone

### Backend
- **Framework**: FastAPI (Python)
- **ML Models**: Scikit-learn, TensorFlow, PyTorch
- **Image Processing**: OpenCV, Pillow
- **Data Visualization**: Matplotlib, Plotly

### Design System
- **Primary Colors**: Deep Navy (#0A1628), Teal (#00C9A7), Electric Blue (#3B82F6)
- **Typography**: Inter font family
- **UI Style**: Glassmorphism with dark mode
- **Animations**: Subtle transitions and loading states

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd medai-diagnostics
```

2. Start all services:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoints

### Disease Prediction
- `POST /api/pneumonia/predict` - Pneumonia detection from X-ray
- `POST /api/malaria/predict` - Malaria detection from blood smear
- `POST /api/breast-cancer/predict` - Breast cancer from clinical features
- `POST /api/diabetes/predict` - Diabetes risk assessment
- `POST /api/alzheimer/predict` - Alzheimer's detection from MRI
- `POST /api/liver-disease/predict` - Liver disease prediction
- `POST /api/kidney-disease/predict` - CKD prediction
- `POST /api/heart-disease/predict` - Heart disease prediction

### Metrics
- `GET /api/metrics/{disease}` - Performance metrics for specific model
- `GET /api/metrics/all` - All model performance comparison

## Model Information

Each disease module uses appropriate ML/DL models:
- **Image-based**: CNN architectures (MobileNetV2, EfficientNetB0)
- **Tabular data**: Random Forest, XGBoost
- **Multi-class**: Softmax classification with 4 categories

## Demo Mode

The platform includes a comprehensive demo mode that:
- Auto-fills forms with sample data
- Runs predictions automatically
- Cycles through all disease modules in presentation mode
- Generates sample reports

## Important Disclaimer

**This tool is for educational and research purposes only and does not constitute medical advice.** Always consult qualified healthcare professionals for medical decisions.

## Project Structure

```
medai-diagnostics/
frontend/
  src/
    app/           # Next.js app router
    components/    # React components
    lib/          # Utility functions
    types/        # TypeScript definitions
    hooks/        # Custom React hooks

backend/
  app/
    models/       # ML model implementations
    routers/      # API route handlers
    services/     # Business logic
    utils/        # Helper functions
    schemas/      # Pydantic models
  data/          # Training datasets
  models/        # Trained model weights
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on the GitHub repository.

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Activity, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { formatConfidence, getRiskColor, getRiskBadgeClass } from "@/lib/utils";
import { API_ENDPOINTS } from "@/lib/api-config";
import { useSession } from "@/context/SessionContext";

interface DiabetesFormData {
  pregnancies: string;
  glucose: string;
  blood_pressure: string;
  skin_thickness: string;
  insulin: string;
  bmi: string;
  diabetes_pedigree: string;
  age: string;
}

interface PredictionResult {
  disease: string;
  confidence: number;
  risk_level: string;
  prediction: string;
  explanation: string;
  diabetic_probability: number;
  non_diabetic_probability: number;
  risk_tier: string;
  top_risk_factors: string[];
  disclaimer: string;
}

export default function DiabetesModule() {
  const [formData, setFormData] = useState<DiabetesFormData>({
    pregnancies: "",
    glucose: "",
    blood_pressure: "",
    skin_thickness: "",
    insulin: "",
    bmi: "",
    diabetes_pedigree: "",
    age: "",
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { addSessionPrediction } = useSession();

  const handleInputChange = (field: keyof DiabetesFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_ENDPOINTS.diabetes}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pregnancies: parseFloat(formData.pregnancies) || 0,
          glucose: parseFloat(formData.glucose) || 0,
          blood_pressure: parseFloat(formData.blood_pressure) || 0,
          skin_thickness: parseFloat(formData.skin_thickness) || 0,
          insulin: parseFloat(formData.insulin) || 0,
          bmi: parseFloat(formData.bmi) || 0,
          diabetes_pedigree: parseFloat(formData.diabetes_pedigree) || 0,
          age: parseFloat(formData.age) || 0,
        }),
      });

      if (!response.ok) {
        throw new Error("Prediction failed");
      }

      const predictionResult = await response.json();
      setResult(predictionResult);

      // Add prediction to current session
      const predictionRecord = {
        disease: "Diabetes",
        prediction: predictionResult.prediction,
        confidence: predictionResult.confidence,
        riskLevel: predictionResult.risk_level,
        explanation: predictionResult.explanation,
        timestamp: new Date().toLocaleString(),
        details: {
          diabeticProbability: predictionResult.diabetic_probability,
          nonDiabeticProbability: predictionResult.non_diabetic_probability,
          riskTier: predictionResult.risk_tier,
        },
        inputs: formData,
      };
      addSessionPrediction(predictionRecord);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    // Fill with demo data
    setFormData({
      pregnancies: "2",
      glucose: "130",
      blood_pressure: "80",
      skin_thickness: "25",
      insulin: "120",
      bmi: "28.5",
      diabetes_pedigree: "0.6",
      age: "45",
    });

    // Auto-submit after a short delay
    setTimeout(() => {
      const event = new Event("submit") as any;
      event.preventDefault = () => {};
      handleSubmit(event);
    }, 500);
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case "low":
        return <CheckCircle className="w-5 h-5 text-green-success" />;
      case "moderate":
        return <AlertTriangle className="w-5 h-5 text-yellow-warning" />;
      case "high":
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case "critical":
        return <XCircle className="w-5 h-5 text-red-alert" />;
      default:
        return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen medical-gradient">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Diabetes Risk Prediction
          </h1>
          <p className="text-gray-300">
            Assess your diabetes risk based on clinical parameters
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="medical-card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-white">
                Clinical Parameters
              </h2>
              <Button onClick={handleDemo} variant="outline" size="sm">
                Demo Mode
              </Button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Number of Pregnancies
                  </label>
                  <input
                    type="number"
                    value={formData.pregnancies}
                    onChange={(e) =>
                      handleInputChange("pregnancies", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="0"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Glucose (mg/dL)
                  </label>
                  <input
                    type="number"
                    value={formData.glucose}
                    onChange={(e) =>
                      handleInputChange("glucose", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="120"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Blood Pressure (mm Hg)
                  </label>
                  <input
                    type="number"
                    value={formData.blood_pressure}
                    onChange={(e) =>
                      handleInputChange("blood_pressure", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="80"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Skin Thickness (mm)
                  </label>
                  <input
                    type="number"
                    value={formData.skin_thickness}
                    onChange={(e) =>
                      handleInputChange("skin_thickness", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="20"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Insulin (mu U/ml)
                  </label>
                  <input
                    type="number"
                    value={formData.insulin}
                    onChange={(e) =>
                      handleInputChange("insulin", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="79"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    BMI
                  </label>
                  <input
                    type="number"
                    value={formData.bmi}
                    onChange={(e) => handleInputChange("bmi", e.target.value)}
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="25.0"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Diabetes Pedigree Function
                  </label>
                  <input
                    type="number"
                    value={formData.diabetes_pedigree}
                    onChange={(e) =>
                      handleInputChange("diabetes_pedigree", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="0.5"
                    step="0.01"
                    min="0"
                    max="2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Age (years)
                  </label>
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => handleInputChange("age", e.target.value)}
                    className="w-full px-3 py-2 bg-navy-medium border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-primary"
                    placeholder="30"
                    step="1"
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-teal-primary hover:bg-teal-secondary"
                disabled={loading}
              >
                {loading ? "Analyzing..." : "Predict Diabetes Risk"}
              </Button>
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-alert/20 border border-red-alert/30 rounded-lg">
                <p className="text-red-alert">{error}</p>
              </div>
            )}
          </div>

          {/* Results */}
          <div className="medical-card">
            <h2 className="text-2xl font-semibold text-white mb-6">
              Prediction Results
            </h2>

            {result ? (
              <div className="space-y-6">
                {/* Risk Badge */}
                <div className="flex items-center space-x-3">
                  {getRiskIcon(result.risk_level)}
                  <span
                    className={`px-4 py-2 rounded-full text-sm font-semibold ${getRiskBadgeClass(result.risk_level)}`}
                  >
                    {result.risk_level} RISK
                  </span>
                  <span className="text-white font-semibold">
                    {formatConfidence(result.confidence)} Confidence
                  </span>
                </div>

                {/* Prediction */}
                <div className="p-4 bg-navy-medium rounded-lg">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Prediction
                  </h3>
                  <p className="text-2xl font-bold text-teal-primary">
                    {result.prediction}
                  </p>
                  <p className="text-gray-300 mt-2">{result.explanation}</p>
                </div>

                {/* Probabilities */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Diabetic Probability</span>
                    <span className="text-white font-semibold">
                      {formatConfidence(result.diabetic_probability)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div
                      className="bg-red-alert h-3 rounded-full transition-all duration-500"
                      style={{ width: `${result.diabetic_probability}%` }}
                    />
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">
                      Non-Diabetic Probability
                    </span>
                    <span className="text-white font-semibold">
                      {formatConfidence(result.non_diabetic_probability)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div
                      className="bg-green-success h-3 rounded-full transition-all duration-500"
                      style={{ width: `${result.non_diabetic_probability}%` }}
                    />
                  </div>
                </div>

                {/* Risk Tier */}
                <div className="p-4 bg-navy-medium rounded-lg">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Risk Assessment
                  </h3>
                  <p className="text-xl font-bold text-yellow-warning">
                    {result.risk_tier}
                  </p>
                </div>

                {/* Top Risk Factors */}
                {result.top_risk_factors &&
                  result.top_risk_factors.length > 0 && (
                    <div className="p-4 bg-navy-medium rounded-lg">
                      <h3 className="text-lg font-semibold text-white mb-3">
                        Top Risk Factors
                      </h3>
                      <ul className="space-y-2">
                        {result.top_risk_factors.map((factor, index) => (
                          <li
                            key={index}
                            className="flex items-center space-x-2"
                          >
                            <div className="w-2 h-2 bg-teal-primary rounded-full" />
                            <span className="text-gray-300">{factor}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* Disclaimer */}
                <div className="p-4 bg-yellow-warning/20 border border-yellow-warning/30 rounded-lg">
                  <p className="text-yellow-warning text-sm">
                    {result.disclaimer}
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Activity className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400">
                  Complete the form and submit to see prediction results
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

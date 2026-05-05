'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

export type Language = 'en' | 'hi'

interface Translations {
  [key: string]: { en: string; hi: string }
}

const translations: Translations = {
  // Navigation
  'nav.home': { en: 'Home', hi: 'होम' },
  'nav.modules': { en: 'Modules', hi: 'मॉड्यूल' },
  'nav.accuracy': { en: 'Accuracy', hi: 'सटीकता' },
  'nav.technology': { en: 'Technology', hi: 'तकनीक' },
  'nav.login': { en: 'Login', hi: 'लॉगिन' },
  'nav.patients': { en: 'Patients', hi: 'मरीज़' },
  'nav.tagline': { en: 'AI-Powered Clinical Intelligence', hi: 'AI-संचालित क्लिनिकल इंटेलिजेंस' },
  'nav.systemMetrics': { en: 'System Metrics', hi: 'सिस्टम मेट्रिक्स' },
  'nav.doctorLogin': { en: 'Doctor Login', hi: 'डॉक्टर लॉगिन' },

  // Hero
  'hero.badge': { en: 'All Systems Operational', hi: 'सभी सिस्टम चालू हैं' },
  'hero.title1': { en: 'Clinical-Grade AI', hi: 'क्लिनिकल-ग्रेड AI' },
  'hero.title2': { en: 'Diagnostic Intelligence', hi: 'डायग्नोस्टिक इंटेलिजेंस' },
  'hero.desc': {
    en: 'A multimodal medical triage platform combining <strong>Computer Vision</strong>, <strong>Random Forest classifiers</strong>, <strong>Explainable AI</strong>, and <strong>Large Language Models</strong> to deliver instant, transparent diagnostic assessments.',
    hi: '<strong>कंप्यूटर विज़न</strong>, <strong>रैंडम फ़ॉरेस्ट क्लासिफायर</strong>, <strong>एक्सप्लेनेबल AI</strong> और <strong>लार्ज लैंग्वेज मॉडल</strong> को जोड़कर तत्काल, पारदर्शी नैदानिक मूल्यांकन देने वाला मल्टीमॉडल मेडिकल ट्राइएज प्लेटफ़ॉर्म।'
  },
  'hero.startDiagnosis': { en: 'Start Diagnosis', hi: 'निदान शुरू करें' },
  'hero.scanSkin': { en: 'Scan Skin Condition', hi: 'त्वचा स्कैन करें' },

  // Module Names & Descriptions
  'modules.title': { en: 'Choose Your Analysis', hi: 'अपना विश्लेषण चुनें' },
  'modules.subtitle': { en: 'Diagnostic Modules', hi: 'डायग्नोस्टिक मॉड्यूल' },
  'modules.launch': { en: 'Launch', hi: 'शुरू करें' },
  'modules.count': { en: '6 AI-powered clinical modules', hi: '6 AI-संचालित क्लिनिकल मॉड्यूल' },

  'mod.symptom.name': { en: 'Smart Symptom Checker', hi: 'स्मार्ट लक्षण परीक्षक' },
  'mod.symptom.desc': { en: 'Interactive 3D body map with Random Forest ML — select symptoms and get instant AI predictions across 41 diseases.', hi: 'रैंडम फ़ॉरेस्ट ML के साथ इंटरैक्टिव 3D बॉडी मैप — लक्षण चुनें और 41 बीमारियों में तत्काल AI भविष्यवाणी प्राप्त करें।' },
  'mod.skin.name': { en: 'Dermatology AI Scanner', hi: 'त्वचा रोग AI स्कैनर' },
  'mod.skin.desc': { en: 'Computer vision skin analysis with Explainable AI saliency maps showing diagnostic attention regions.', hi: 'एक्सप्लेनेबल AI सैलिएंसी मैप के साथ कंप्यूटर विज़न त्वचा विश्लेषण जो नैदानिक ​​ध्यान क्षेत्रों को दिखाता है।' },
  'mod.ai.name': { en: 'Clinical AI Consultant', hi: 'क्लिनिकल AI सलाहकार' },
  'mod.ai.desc': { en: 'Context-aware medical Q&A powered by Llama 3 with Retrieval-Augmented Generation from your diagnostic session.', hi: 'Llama 3 द्वारा संचालित संदर्भ-जागरूक चिकित्सा प्रश्नोत्तर, आपके नैदानिक सत्र से रिट्रीवल-ऑगमेंटेड जनरेशन के साथ।' },
  'mod.mlops.name': { en: 'MLOps Control Center', hi: 'MLOps नियंत्रण केंद्र' },
  'mod.mlops.desc': { en: 'Production-grade model monitoring with data drift detection, feedback loops, and continuous learning pipeline visualization.', hi: 'डेटा ड्रिफ्ट डिटेक्शन, फीडबैक लूप और कंटीन्यूअस लर्निंग पाइपलाइन विज़ुअलाइज़ेशन के साथ प्रोडक्शन-ग्रेड मॉडल मॉनिटरिंग।' },
  'mod.patient.name': { en: 'Patient Management', hi: 'मरीज़ प्रबंधन' },
  'mod.patient.desc': { en: 'Complete patient records, consultation history, and clinical data management with doctor authentication.', hi: 'डॉक्टर प्रमाणीकरण के साथ पूर्ण मरीज़ रिकॉर्ड, परामर्श इतिहास और क्लिनिकल डेटा प्रबंधन।' },
  'mod.rx.name': { en: 'Prescription Generator', hi: 'प्रिस्क्रिप्शन जनरेटर' },
  'mod.rx.desc': { en: 'Generate professional prescriptions with medicine details, dosage, frequency, and clinic-branded PDF export.', hi: 'दवा विवरण, खुराक, आवृत्ति और क्लिनिक-ब्रांडेड PDF निर्यात के साथ पेशेवर प्रिस्क्रिप्शन बनाएं।' },

  // Platform Stats
  'stat.symptomAcc': { en: 'Symptom Model Accuracy', hi: 'लक्षण मॉडल सटीकता' },
  'stat.skinAcc': { en: 'Skin CV Engine Accuracy', hi: 'त्वचा CV इंजन सटीकता' },
  'stat.conditions': { en: 'Diagnosable Conditions', hi: 'निदान योग्य स्थितियाँ' },
  'stat.responseTime': { en: 'Average Response Time', hi: 'औसत प्रतिक्रिया समय' },

  // Symptom Checker Page
  'symptom.title': { en: 'Smart Symptom Checker', hi: 'स्मार्ट लक्षण परीक्षक' },
  'symptom.desc': { en: 'Select symptoms using the interactive 3D body map or the dropdown menu.', hi: '3D बॉडी मैप या ड्रॉपडाउन मेन्यू से लक्षण चुनें।' },
  'symptom.bodyMap': { en: '3D Body Map', hi: '3D बॉडी मैप' },
  'symptom.dropdown': { en: 'Dropdown List', hi: 'ड्रॉपडाउन सूची' },
  'symptom.yourSymptoms': { en: 'Your Symptoms', hi: 'आपके लक्षण' },
  'symptom.analyze': { en: 'Analyze Symptoms', hi: 'लक्षण विश्लेषण करें' },
  'symptom.analyzing': { en: 'AI is analyzing...', hi: 'AI विश्लेषण कर रहा है...' },
  'symptom.result': { en: 'Analysis Result', hi: 'विश्लेषण परिणाम' },
  'symptom.confidence': { en: 'AI Confidence', hi: 'AI विश्वास स्तर' },
  'symptom.severity': { en: 'Severity Level', hi: 'गंभीरता स्तर' },
  'symptom.recommendation': { en: 'Recommendation', hi: 'सिफारिश' },

  // Skin Analyzer Page
  'skin.title': { en: 'Skin Infection Analyzer', hi: 'त्वचा संक्रमण विश्लेषक' },
  'skin.upload': { en: 'Upload or capture a clear photo', hi: 'एक स्पष्ट फोटो अपलोड या कैप्चर करें' },
  'skin.analyzing': { en: 'AI is analyzing the image...', hi: 'AI छवि का विश्लेषण कर रहा है...' },
  'skin.result': { en: 'Skin Analysis Result', hi: 'त्वचा विश्लेषण परिणाम' },
  'skin.heatmap': { en: 'XAI Attention Heatmap', hi: 'XAI ध्यान हीटमैप' },

  // AI Assistant Page
  'ai.title': { en: 'AI Clinical Consultant', hi: 'AI क्लिनिकल सलाहकार' },
  'ai.placeholder': { en: 'Ask a medical question...', hi: 'चिकित्सा प्रश्न पूछें...' },
  'ai.send': { en: 'Send', hi: 'भेजें' },
  'ai.thinking': { en: 'AI is thinking...', hi: 'AI सोच रहा है...' },

  // MLOps Dashboard
  'mlops.title': { en: 'MLOps Dashboard', hi: 'MLOps डैशबोर्ड' },
  'mlops.performance': { en: 'Live Model Performance', hi: 'लाइव मॉडल प्रदर्शन' },
  'mlops.feedback': { en: 'User Feedback', hi: 'उपयोगकर्ता प्रतिक्रिया' },
  'mlops.trained': { en: 'Trained', hi: 'प्रशिक्षित' },
  'mlops.notTrained': { en: 'Not Trained', hi: 'अप्रशिक्षित' },
  'mlops.accuracy': { en: 'Validation Accuracy', hi: 'सत्यापन सटीकता' },

  // Prescription Page
  'rx.title': { en: 'Prescription Generator', hi: 'प्रिस्क्रिप्शन जनरेटर' },
  'rx.medicine': { en: 'Medicine Name', hi: 'दवा का नाम' },
  'rx.dosage': { en: 'Dosage', hi: 'खुराक' },
  'rx.duration': { en: 'Duration', hi: 'अवधि' },
  'rx.frequency': { en: 'Frequency', hi: 'आवृत्ति' },
  'rx.download': { en: 'Download Prescription', hi: 'प्रिस्क्रिप्शन डाउनलोड करें' },
  'rx.add': { en: 'Add Medicine', hi: 'दवा जोड़ें' },
  'rx.patientName': { en: 'Patient Name', hi: 'मरीज़ का नाम' },
  'rx.diagnosis': { en: 'Diagnosis', hi: 'निदान' },
  'rx.notes': { en: 'Notes', hi: 'टिप्पणियाँ' },

  // Patient Management Page
  'patient.name': { en: 'Patient Name', hi: 'मरीज़ का नाम' },
  'patient.age': { en: 'Age', hi: 'उम्र' },
  'patient.gender': { en: 'Gender', hi: 'लिंग' },
  'patient.phone': { en: 'Phone', hi: 'फोन' },
  'patient.bloodGroup': { en: 'Blood Group', hi: 'रक्त समूह' },
  'patient.addNew': { en: 'Add New Patient', hi: 'नया मरीज़ जोड़ें' },
  'patient.history': { en: 'Medical History', hi: 'चिकित्सा इतिहास' },
  'patient.allergies': { en: 'Allergies', hi: 'एलर्जी' },
  'patient.dashboard': { en: 'Patient Dashboard', hi: 'मरीज़ डैशबोर्ड' },

  // Common
  'common.back': { en: 'Back', hi: 'वापस' },
  'common.save': { en: 'Save', hi: 'सेव करें' },
  'common.cancel': { en: 'Cancel', hi: 'रद्द करें' },
  'common.delete': { en: 'Delete', hi: 'हटाएं' },
  'common.search': { en: 'Search', hi: 'खोजें' },
  'common.loading': { en: 'Loading...', hi: 'लोड हो रहा है...' },
  'common.noData': { en: 'No data found', hi: 'कोई डेटा नहीं मिला' },
  'common.language': { en: 'Language', hi: 'भाषा' },
  'common.submit': { en: 'Submit', hi: 'जमा करें' },

  // Auth
  'auth.login': { en: 'Sign In', hi: 'साइन इन' },
  'auth.register': { en: 'Register', hi: 'रजिस्टर करें' },
  'auth.email': { en: 'Email', hi: 'ईमेल' },
  'auth.password': { en: 'Password', hi: 'पासवर्ड' },
  'auth.doctorName': { en: 'Doctor Name', hi: 'डॉक्टर का नाम' },
  'auth.clinicName': { en: 'Clinic Name', hi: 'क्लिनिक का नाम' },
  'auth.specialization': { en: 'Specialization', hi: 'विशेषज्ञता' },
  'auth.logout': { en: 'Logout', hi: 'लॉगआउट' },
  'auth.welcome': { en: 'Welcome back, Doctor', hi: 'वापसी पर स्वागत, डॉक्टर' },
  'auth.noAccount': { en: 'No account? Register', hi: 'खाता नहीं है? रजिस्टर करें' },
  'auth.haveAccount': { en: 'Already have an account? Sign In', hi: 'पहले से खाता है? साइन इन करें' },

  // Stats
  'stats.totalPatients': { en: 'Total Patients', hi: 'कुल मरीज़' },
  'stats.todayConsultations': { en: "Today's Consultations", hi: 'आज की परामर्श' },
  'stats.totalConsultations': { en: 'Total Consultations', hi: 'कुल परामर्श' },

  // Tech Section
  'tech.title': { en: 'Technology Stack', hi: 'तकनीकी स्टैक' },
  'tech.subtitle': { en: 'Built with Production-Grade Architecture', hi: 'प्रोडक्शन-ग्रेड आर्किटेक्चर के साथ निर्मित' },

  // Footer
  'footer.disclaimer': { en: 'AI-assisted diagnostic tool for educational purposes. Not a substitute for professional medical advice.', hi: 'शैक्षिक उद्देश्यों के लिए AI-सहायित नैदानिक उपकरण। पेशेवर चिकित्सा सलाह का विकल्प नहीं।' },
}

interface LanguageContextType {
  lang: Language
  setLang: (lang: Language) => void
  t: (key: string) => string
}

const LanguageContext = createContext<LanguageContextType>({
  lang: 'en',
  setLang: () => {},
  t: (key: string) => key,
})

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Language>('en')

  const t = (key: string): string => {
    return translations[key]?.[lang] || key
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = () => useContext(LanguageContext)

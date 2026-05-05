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

  // Hero
  'hero.badge': { en: 'All Systems Operational', hi: 'सभी सिस्टम चालू हैं' },
  'hero.title1': { en: 'Clinical-Grade AI', hi: 'क्लिनिकल-ग्रेड AI' },
  'hero.title2': { en: 'Diagnostic Intelligence', hi: 'डायग्नोस्टिक इंटेलिजेंस' },
  'hero.desc': {
    en: 'A multimodal medical triage platform combining Computer Vision, Random Forest classifiers, Explainable AI, and Large Language Models.',
    hi: 'कंप्यूटर विज़न, रैंडम फ़ॉरेस्ट क्लासिफायर, एक्सप्लेनेबल AI और लार्ज लैंग्वेज मॉडल को जोड़ने वाला मल्टीमॉडल मेडिकल ट्राइएज प्लेटफ़ॉर्म।'
  },
  'hero.startDiagnosis': { en: 'Start Diagnosis', hi: 'निदान शुरू करें' },
  'hero.scanSkin': { en: 'Scan Skin Condition', hi: 'त्वचा स्कैन करें' },

  // Modules
  'modules.title': { en: 'Choose Your Analysis', hi: 'अपना विश्लेषण चुनें' },
  'modules.subtitle': { en: 'Diagnostic Modules', hi: 'डायग्नोस्टिक मॉड्यूल' },
  'modules.launch': { en: 'Launch', hi: 'शुरू करें' },

  // Symptom Checker
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

  // Skin Analyzer
  'skin.title': { en: 'Skin Infection Analyzer', hi: 'त्वचा संक्रमण विश्लेषक' },
  'skin.upload': { en: 'Upload or capture a clear photo', hi: 'एक स्पष्ट फोटो अपलोड या कैप्चर करें' },

  // Prescription
  'rx.title': { en: 'Prescription Generator', hi: 'प्रिस्क्रिप्शन जनरेटर' },
  'rx.medicine': { en: 'Medicine Name', hi: 'दवा का नाम' },
  'rx.dosage': { en: 'Dosage', hi: 'खुराक' },
  'rx.duration': { en: 'Duration', hi: 'अवधि' },
  'rx.frequency': { en: 'Frequency', hi: 'आवृत्ति' },
  'rx.download': { en: 'Download Prescription', hi: 'प्रिस्क्रिप्शन डाउनलोड करें' },
  'rx.add': { en: 'Add Medicine', hi: 'दवा जोड़ें' },

  // Patient Management
  'patient.name': { en: 'Patient Name', hi: 'मरीज़ का नाम' },
  'patient.age': { en: 'Age', hi: 'उम्र' },
  'patient.gender': { en: 'Gender', hi: 'लिंग' },
  'patient.phone': { en: 'Phone', hi: 'फोन' },
  'patient.bloodGroup': { en: 'Blood Group', hi: 'रक्त समूह' },
  'patient.addNew': { en: 'Add New Patient', hi: 'नया मरीज़ जोड़ें' },
  'patient.history': { en: 'Medical History', hi: 'चिकित्सा इतिहास' },

  // Common
  'common.back': { en: 'Back', hi: 'वापस' },
  'common.save': { en: 'Save', hi: 'सेव करें' },
  'common.cancel': { en: 'Cancel', hi: 'रद्द करें' },
  'common.delete': { en: 'Delete', hi: 'हटाएं' },
  'common.search': { en: 'Search', hi: 'खोजें' },
  'common.loading': { en: 'Loading...', hi: 'लोड हो रहा है...' },
  'common.noData': { en: 'No data found', hi: 'कोई डेटा नहीं मिला' },
  'common.language': { en: 'Language', hi: 'भाषा' },

  // Auth
  'auth.login': { en: 'Sign In', hi: 'साइन इन' },
  'auth.register': { en: 'Register', hi: 'रजिस्टर करें' },
  'auth.email': { en: 'Email', hi: 'ईमेल' },
  'auth.password': { en: 'Password', hi: 'पासवर्ड' },
  'auth.doctorName': { en: 'Doctor Name', hi: 'डॉक्टर का नाम' },
  'auth.clinicName': { en: 'Clinic Name', hi: 'क्लिनिक का नाम' },
  'auth.specialization': { en: 'Specialization', hi: 'विशेषज्ञता' },
  'auth.logout': { en: 'Logout', hi: 'लॉगआउट' },

  // Stats
  'stats.totalPatients': { en: 'Total Patients', hi: 'कुल मरीज़' },
  'stats.todayConsultations': { en: "Today's Consultations", hi: 'आज की परामर्श' },
  'stats.totalConsultations': { en: 'Total Consultations', hi: 'कुल परामर्श' },
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

export type ScreeningField = {
  key: string;
  label: string;
  type: "profile" | "symptom" | "measurement" | "report";
  question: string;
  help?: string;
};

export const SCREENING_CONFIG: Record<string, ScreeningField[]> = {
  diabetes: [
    {
      key: "age",
      label: "Age",
      type: "profile",
      question: "How old are you?"
    },
    {
      key: "bmi",
      label: "Body size",
      type: "profile",
      question: "We'll calculate this automatically from your height and weight."
    },
    {
      key: "glucose",
      label: "Blood sugar",
      type: "report",
      question: "Do you have a recent blood-test report?",
      help: "You don't need to know your blood-sugar number. Upload the report and we'll look for the relevant information."
    },
    {
      key: "blood_pressure",
      label: "Blood pressure",
      type: "measurement",
      question: "Do you know your recent blood-pressure reading?",
      help: "For example, 120/80."
    }
  ],

  heart_disease: [
    {
      key: "age",
      label: "Age",
      type: "profile",
      question: "How old are you?"
    },
    {
      key: "chest_discomfort",
      label: "Chest discomfort",
      type: "symptom",
      question: "Have you experienced chest discomfort or pressure?",
      help: "You don't need to know the medical term for it."
    },
    {
      key: "shortness_of_breath",
      label: "Breathing",
      type: "symptom",
      question: "Do you get short of breath more easily than usual?"
    },
    {
      key: "heart_report",
      label: "Heart report",
      type: "report",
      question: "Do you have a recent ECG or heart-test report?",
      help: "Upload it if you have one. You don't need to understand the medical numbers."
    }
  ],

  hypertension: [
    {
      key: "age",
      label: "Age",
      type: "profile",
      question: "How old are you?"
    },
    {
      key: "bmi",
      label: "Body size",
      type: "profile",
      question: "We'll calculate this automatically from your height and weight."
    },
    {
      key: "blood_pressure",
      label: "Blood pressure",
      type: "measurement",
      question: "Do you know your recent blood-pressure reading?",
      help: "For example, 120/80. If you don't know it, you can use a recent medical report."
    },
    {
      key: "blood_pressure_report",
      label: "Blood-pressure report",
      type: "report",
      question: "Don't know your blood-pressure numbers?",
      help: "Upload a recent medical report instead."
    }
  ],

  anemia: [
    {
      key: "age",
      label: "Age",
      type: "profile",
      question: "How old are you?"
    },
    {
      key: "blood_test_report",
      label: "Blood test",
      type: "report",
      question: "Do you have a recent blood-test report?",
      help: "MedPulse can use the relevant blood information. You don't need to know terms like MCH, MCHC or MCV."
    }
  ]
};

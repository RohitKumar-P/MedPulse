export type QuestionSource =
  | "profile"
  | "symptom"
  | "lifestyle"
  | "measurement"
  | "medical_report";

export type HealthQuestion = {
  id: string;
  text: string;
  help?: string;
  type: "single" | "number" | "text" | "upload";
  options?: string[];
  source: QuestionSource;
  required?: boolean;
  condition?: (answers: Record<string, unknown>) => boolean;
  internalFeature?: string;
};

export const COMMON_QUESTIONS: HealthQuestion[] = [
  {
    id: "unusual_tiredness",
    text: "Have you been feeling unusually tired lately?",
    help: "Especially if you feel tired even after getting enough rest.",
    type: "single",
    options: ["No", "Sometimes", "Often", "Almost every day"],
    source: "symptom",
  },
  {
    id: "unusual_thirst",
    text: "Have you been much thirstier than usual?",
    type: "single",
    options: ["No", "Sometimes", "Often", "Almost every day"],
    source: "symptom",
  },
  {
    id: "frequent_urination",
    text: "Have you been needing to urinate more often than usual?",
    type: "single",
    options: ["No", "Sometimes", "Often", "Almost every day"],
    source: "symptom",
  },
  {
    id: "dizziness",
    text: "Have you been feeling dizzy or light-headed?",
    type: "single",
    options: ["No", "Sometimes", "Often", "Frequently"],
    source: "symptom",
  },
  {
    id: "shortness_of_breath",
    text: "Have you been getting short of breath more easily than usual?",
    type: "single",
    options: ["No", "Sometimes", "Often", "Frequently"],
    source: "symptom",
  },
  {
    id: "chest_discomfort",
    text: "Have you experienced chest discomfort or pressure?",
    type: "single",
    options: ["No", "Sometimes", "Often", "Frequently"],
    source: "symptom",
  },
  {
    id: "sleep_quality",
    text: "How would you describe your sleep recently?",
    type: "single",
    options: ["Good", "Okay", "Poor", "Very poor"],
    source: "lifestyle",
  },
  {
    id: "physical_activity",
    text: "How physically active are you during a typical week?",
    type: "single",
    options: [
      "Very active",
      "Moderately active",
      "A little active",
      "Mostly inactive",
    ],
    source: "lifestyle",
  },
];

export const REPORT_QUESTIONS: HealthQuestion[] = [
  {
    id: "blood_test_report",
    text: "Do you have a recent blood-test report?",
    help: "You don't need to understand the medical numbers. MedPulse can use the relevant information from the report.",
    type: "upload",
    source: "medical_report",
  },
  {
    id: "heart_test_report",
    text: "Do you have a recent ECG or heart-test report?",
    help: "Only upload this if you have one. You do not need to know the medical terminology.",
    type: "upload",
    source: "medical_report",
  },
];

export const DISEASE_RULES: Record<
  string,
  {
    reports?: string[];
    extraQuestions?: HealthQuestion[];
  }
> = {
  diabetes: {
    reports: ["blood_test_report"],
    extraQuestions: [
      {
        id: "diabetes_family_history",
        text: "Has a close family member had diabetes?",
        type: "single",
        options: ["No", "Yes", "I'm not sure"],
        source: "symptom",
        internalFeature: "diabetes_pedigree",
      },
      {
        id: "pregnancy_history",
        text: "Have you ever been pregnant?",
        help: "This question is only shown when it is relevant to your profile.",
        type: "single",
        options: ["No", "Yes"],
        source: "profile",
        condition: (answers) => answers.sex === "female",
        internalFeature: "pregnancies",
      },
    ],
  },

  heart_disease: {
    reports: ["heart_test_report"],
    extraQuestions: [
      {
        id: "exercise_chest_discomfort",
        text: "Do you ever get chest discomfort during physical activity?",
        type: "single",
        options: ["No", "Sometimes", "Often", "I don't know"],
        source: "symptom",
        internalFeature: "exang",
      },
    ],
  },
};

export function getQuestions(
  disease: string,
  answers: Record<string, unknown>
): HealthQuestion[] {
  const key = disease.toLowerCase().replace(/[\s-]+/g, "_");

  const rules = DISEASE_RULES[key];

  const questions = [
    ...COMMON_QUESTIONS,
    ...(rules?.extraQuestions || []),
  ];

  return questions.filter(
    (question) => !question.condition || question.condition(answers)
  );
}

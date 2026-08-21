import { useState } from "react";
import { Activity, ArrowRight, CheckCircle2, ChevronLeft } from "lucide-react";

type Question = {
  id: string;
  question: string;
  help?: string;
  options: string[];
};

const questions: Question[] = [
  {
    id: "thirst",
    question: "Have you been unusually thirsty lately?",
    help: "More thirsty than what is normal for you.",
    options: ["Never", "Sometimes", "Often", "Almost every day"],
  },
  {
    id: "urination",
    question: "Have you been urinating more often than usual?",
    options: ["No", "Sometimes", "Often", "Very often"],
  },
  {
    id: "fatigue",
    question: "Have you been feeling unusually tired?",
    help: "Especially when you have had enough rest.",
    options: ["No", "Sometimes", "Often", "Almost every day"],
  },
  {
    id: "breathing",
    question: "Do you sometimes feel short of breath?",
    options: ["No", "Sometimes", "Often", "Frequently"],
  },
  {
    id: "dizziness",
    question: "Have you been experiencing dizziness or light-headedness?",
    options: ["No", "Sometimes", "Often", "Frequently"],
  },
  {
    id: "headache",
    question: "Have you been having headaches more often than usual?",
    options: ["No", "Sometimes", "Often", "Frequently"],
  },
  {
    id: "sleep",
    question: "How would you describe your sleep recently?",
    options: ["Good", "Okay", "Poor", "Very poor"],
  },
  {
    id: "activity",
    question: "How physically active are you in a typical week?",
    options: ["Very active", "Moderately active", "A little active", "Mostly inactive"],
  },
];

export default function SymptomScreening({
  onNavigate,
}: {
  onNavigate: (page: any) => void;
}) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const current = questions[step];
  const selected = answers[current.id];

  const choose = (value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [current.id]: value,
    }));
  };

  const next = () => {
    if (!selected) return;

    if (step < questions.length - 1) {
      setStep((value) => value + 1);
    } else {
      localStorage.setItem(
        "medpulse-symptom-screening",
        JSON.stringify(answers)
      );
      onNavigate("result");
    }
  };

  const back = () => {
    if (step > 0) {
      setStep((value) => value - 1);
    } else {
      onNavigate("dashboard");
    }
  };

  return (
    <section className="min-h-screen bg-[#f6f9fc] px-5 py-10 lg:px-8">
      <div className="mx-auto max-w-4xl">

        <button
          onClick={back}
          className="mb-8 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
        >
          <ChevronLeft size={18} />
          Back
        </button>

        <div className="rounded-[2rem] bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-10">

          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm font-bold text-cyan-600">
                <Activity size={18} />
                MEDPULSE SCREENING
              </div>

              <h1 className="mt-3 text-3xl font-black text-slate-900">
                Tell us how you feel
              </h1>

              <p className="mt-2 text-slate-500">
                No medical knowledge required. Answer simple questions about
                your symptoms and everyday health.
              </p>
            </div>

            <div className="hidden rounded-2xl bg-cyan-50 px-4 py-3 text-center sm:block">
              <div className="text-xl font-black text-cyan-700">
                {step + 1}/{questions.length}
              </div>
              <div className="text-xs font-semibold text-cyan-600">
                QUESTIONS
              </div>
            </div>
          </div>

          <div className="mt-8 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-cyan-400 transition-all duration-300"
              style={{
                width: `${((step + 1) / questions.length) * 100}%`,
              }}
            />
          </div>

          <div className="mt-12">
            <span className="text-sm font-bold text-cyan-600">
              Question {step + 1}
            </span>

            <h2 className="mt-3 text-2xl font-black leading-tight text-slate-900 sm:text-3xl">
              {current.question}
            </h2>

            {current.help && (
              <p className="mt-3 text-slate-500">
                {current.help}
              </p>
            )}

            <div className="mt-8 grid gap-3">
              {current.options.map((option) => {
                const active = selected === option;

                return (
                  <button
                    key={option}
                    onClick={() => choose(option)}
                    className={`flex items-center justify-between rounded-2xl border p-5 text-left transition ${
                      active
                        ? "border-cyan-400 bg-cyan-50 ring-2 ring-cyan-100"
                        : "border-slate-200 bg-white hover:border-cyan-200 hover:bg-slate-50"
                    }`}
                  >
                    <span
                      className={`font-semibold ${
                        active ? "text-cyan-800" : "text-slate-700"
                      }`}
                    >
                      {option}
                    </span>

                    {active && (
                      <CheckCircle2
                        size={21}
                        className="text-cyan-600"
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-10 flex justify-end">
            <button
              onClick={next}
              disabled={!selected}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-6 py-3.5 font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {step === questions.length - 1
                ? "View Screening Result"
                : "Continue"}
              <ArrowRight size={18} />
            </button>
          </div>

        </div>

        <p className="mx-auto mt-5 max-w-2xl text-center text-xs leading-5 text-slate-400">
          MedPulse provides screening and risk estimates, not medical
          diagnoses. Your answers should not replace advice from a qualified
          healthcare professional.
        </p>

      </div>
    </section>
  );
}





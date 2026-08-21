import { Activity, ArrowRight, HeartPulse, ShieldCheck, Stethoscope } from "lucide-react";

type DashboardProps = {
  onNavigate: (page: any) => void;
};

export default function HealthDashboard({ onNavigate }: DashboardProps) {
  const lastResult = (() => {
    try {
      return JSON.parse(
        localStorage.getItem("medpulse-last-result") || "null"
      );
    } catch {
      return null;
    }
  })();

  const assessments = (() => {
    try {
      return JSON.parse(
        localStorage.getItem("medpulse-history") || "[]"
      );
    } catch {
      return [];
    }
  })();

  const profile = (() => {
    try {
      return JSON.parse(
        localStorage.getItem("medpulse-profile") || "{}"
      );
    } catch {
      return {};
    }
  })();

  const risk = lastResult?.risk ?? lastResult?.probability ?? null;

  return (
    <section className="min-h-screen bg-[#f6f9fc] px-5 py-10 lg:px-8">
      <div className="mx-auto max-w-7xl">

        <div className="mb-8">
          <p className="text-sm font-semibold text-cyan-600">
            MEDPULSE HEALTH INTELLIGENCE
          </p>

          <h1 className="mt-2 text-3xl font-black text-slate-900">
            Your Health Dashboard
          </h1>

          <p className="mt-2 text-slate-500">
            A simple view of your screenings, health data and recent activity.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-500">
                Health Status
              </span>
              <HeartPulse className="text-cyan-600" size={22} />
            </div>

            <div className="mt-6 text-2xl font-black text-slate-900">
              {lastResult ? "Screened" : "Not screened"}
            </div>

            <p className="mt-2 text-sm text-slate-500">
              {lastResult
                ? "Your latest screening is available."
                : "Complete your first screening."}
            </p>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-500">
                Latest Risk
              </span>
              <ShieldCheck className="text-cyan-600" size={22} />
            </div>

            <div className="mt-6 text-2xl font-black text-slate-900">
              {risk !== null ? `${Math.round(Number(risk) * 100)}%` : "--"}
            </div>

            <p className="mt-2 text-sm text-slate-500">
              Based on your latest available result.
            </p>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-500">
                Assessments
              </span>
              <Activity className="text-cyan-600" size={22} />
            </div>

            <div className="mt-6 text-2xl font-black text-slate-900">
              {assessments.length}
            </div>

            <p className="mt-2 text-sm text-slate-500">
              Recorded health assessments.
            </p>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-500">
                Profile
              </span>
              <Stethoscope className="text-cyan-600" size={22} />
            </div>

            <div className="mt-6 text-2xl font-black text-slate-900">
              {profile.name || "Complete"}
            </div>

            <p className="mt-2 text-sm text-slate-500">
              Your health profile.
            </p>
          </div>

        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-[1.4fr_.6fr]">

          <div className="rounded-3xl bg-slate-900 p-8 text-white">
            <p className="text-sm font-semibold text-cyan-300">
              QUICK ACTION
            </p>

            <h2 className="mt-3 text-2xl font-black">
              Check your health risk
            </h2>

            <p className="mt-3 max-w-xl leading-7 text-slate-300">
              Choose a disease screening and provide the required health
              information. MedPulse uses disease-specific machine learning
              models to generate a risk estimate.
            </p>

            <button
              onClick={() => onNavigate("screening")}
              className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-5 py-3 font-bold text-slate-950 hover:bg-cyan-300"
            >
              Start Screening
              <ArrowRight size={18} />
            </button>
          </div>

          <div className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
            <p className="text-sm font-semibold text-slate-500">
              RECENT ACTIVITY
            </p>

            {assessments.length === 0 ? (
              <div className="mt-8">
                <p className="font-bold text-slate-900">
                  No assessments yet
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Your completed screenings will appear here.
                </p>
              </div>
            ) : (
              <div className="mt-6 space-y-3">
                {assessments.slice(-4).reverse().map(
                  (item: any, index: number) => (
                    <div
                      key={index}
                      className="rounded-2xl bg-slate-50 p-4"
                    >
                      <div className="font-bold text-slate-800">
                        {item.disease || item.name || "Health Assessment"}
                      </div>

                      <div className="mt-1 text-xs text-slate-500">
                        {item.date || "Recent assessment"}
                      </div>
                    </div>
                  )
                )}
              </div>
            )}
          </div>

        </div>

        <div className="mt-8 grid gap-5 md:grid-cols-3">

          <button
            onClick={() => onNavigate("trends")}
            className="rounded-3xl bg-white p-6 text-left shadow-sm ring-1 ring-slate-200 hover:ring-cyan-300"
          >
            <Activity className="text-cyan-600" />
            <h3 className="mt-5 font-black text-slate-900">
              Health Trends
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Track how your health indicators change over time.
            </p>
          </button>

          <button
            onClick={() => onNavigate("assistant")}
            className="rounded-3xl bg-white p-6 text-left shadow-sm ring-1 ring-slate-200 hover:ring-cyan-300"
          >
            <Stethoscope className="text-cyan-600" />
            <h3 className="mt-5 font-black text-slate-900">
              AI Health Assistant
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Understand your screening results in simpler language.
            </p>
          </button>

          <button
            onClick={() => onNavigate("band")}
            className="rounded-3xl bg-white p-6 text-left shadow-sm ring-1 ring-slate-200 hover:ring-cyan-300"
          >
            <HeartPulse className="text-cyan-600" />
            <h3 className="mt-5 font-black text-slate-900">
              Wearable Health Data
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              View the future wearable integration and tracked vitals.
            </p>
          </button>

        </div>

      </div>
    </section>
  );
}





import { SCREENING_CONFIG } from "./screeningConfig";
import MedicalReportUpload from "./components/MedicalReportUpload";
import { getQuestions, type HealthQuestion } from "./healthQuestionEngine";
import {
  Activity,
  AlertCircle,
  ArrowRight,
  BarChart3,
  Bell,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Clock3,
  Droplets,
  FileHeart,
  Gauge,
  HeartPulse,
  History,
  House,
  Info,
  Leaf,
  LockKeyhole,
  LogIn,
  LogOut,
  Menu,
  MessageCircle,
  Moon,
  Plus,
  RefreshCw,
  Scale,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Sun,
  Thermometer,
  User,
  UserPlus,
  Watch,
  Weight,
  X,
  Zap,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { api, ApiError, DiseaseSchema, PredictionResult } from "./api";

type Page = "onboarding" | "home" | "login" | "register" | "dashboard" | "screening" | "result"
  | "trends" | "assistant" | "band" | "history" | "profile" | "settings";

type UserProfile = { name: string; username: string; age: string; height: string; weight: string };
type StoredAssessment = PredictionResult & { date: string };

const diseases = [
  { id: "diabetes", name: "Diabetes", icon: Droplets, blurb: "Check common signs and risk factors linked with diabetes." },
  { id: "heart", name: "Heart Disease", icon: HeartPulse, blurb: "Check common signs and risk factors related to heart health." },
  { id: "hypertension", name: "Hypertension", icon: Gauge, blurb: "Check patterns that may be linked with high blood pressure." },
  { id: "anemia", name: "Anemia", icon: Activity, blurb: "Check common signs that may be linked with low blood health." },
  { id: "breast-cancer", name: "Breast Cancer", icon: ShieldCheck, blurb: "Check information that may indicate a need for further evaluation." },
  { id: "ckd", name: "Chronic Kidney Disease", icon: Droplets, blurb: "Check signs and information related to kidney health." },
  { id: "liver", name: "Liver Disease", icon: Stethoscope, blurb: "Check signs and information related to liver health." },
  { id: "parkinsons", name: "Parkinson's", icon: BrainCircuit, blurb: "Check information that may indicate a need for further evaluation." },
  { id: "stroke", name: "Stroke Risk", icon: AlertCircle, blurb: "Potential stroke risk estimate from model inputs." },
  { id: "thyroid", name: "Thyroid", icon: Thermometer, blurb: "ML-based thyroid disorder screening estimate." },
];

const featureLabels: Record<string, string> = {
  pregnancies: "Number of pregnancies (if applicable)",
  glucose: "Blood sugar level",
  blood_pressure: "Blood pressure",
  skin_thickness: "Skin-fold measurement (if measured)",
  insulin: "Insulin level (if measured)",
  bmi: "Body mass index",
  diabetes_pedigree: "Family history of diabetes",
  age: "Age",
  sex: "Sex",
  cp: "What kind of chest discomfort do you experience?",
  trestbps: "Resting blood pressure",
  chol: "Total cholesterol level",
  fbs: "Fasting blood sugar",
  restecg: "ECG result",
  thalach: "Maximum heart rate recorded",
  exang: "Chest discomfort during exercise",
  oldpeak: "Exercise ECG measurement",
  slope: "Exercise ECG pattern",
  ca: "Number of major blood vessels from heart test",
  thal: "Thalassemia test result",
  weight: "Weight",
  height: "Height",
};


const optionLabels: Record<string, Record<string, string>> = {
  sex: {
    "0": "Female",
    "1": "Male",
  },
  fbs: {
    "0": "No / normal",
    "1": "Yes / elevated",
  },
  exang: {
    "0": "No",
    "1": "Yes",
  },
  cp: {
    "0": "Typical chest discomfort",
    "1": "Atypical chest discomfort",
    "2": "Other chest discomfort",
    "3": "No chest discomfort",
  },
  restecg: {
    "0": "Normal",
    "1": "Abnormal result",
    "2": "Other abnormal result",
  },
  slope: {
    "0": "Upward pattern",
    "1": "Flat pattern",
    "2": "Downward pattern",
  },
  ca: {
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
  },
  thal: {
    "0": "Not specified",
    "1": "Normal",
    "2": "Fixed abnormality",
    "3": "Reversible abnormality",
  },
};
const selectOptions: Record<string, string[]> = {
  sex: ["0", "1"],
  fbs: ["0", "1"],
  exang: ["0", "1"],
  cp: ["0", "1", "2", "3"],
  restecg: ["0", "1", "2"],
  slope: ["0", "1", "2"],
  ca: ["0", "1", "2", "3"],
  thal: ["0", "1", "2", "3"],
};

const navigate = (target: Page) => {
  window.location.hash = `#/${target}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const getPath = () => {
  const hash = window.location.hash.replace(/^#\/?/, "") || "home";

  if (
    hash === "how" ||
    hash === "screenings" ||
    hash === "tracking"
  ) {
    return "home";
  }

  const validPages = [
    "home",
    "login",
    "register",
    "onboarding",
    "dashboard",
    "screening",
    "result",
    "trends",
    "assistant",
    "band",
    "history",
    "profile",
    "settings"
  ];

  return validPages.includes(hash) ? hash as Page : "home";
};

function App() {
  const [page, setPage] = useState<Page>(getPath());
  const [profile, setProfile] = useState<UserProfile>(() => {
    try { return JSON.parse(localStorage.getItem("medpulse-profile") || "") as UserProfile; }
    catch { return { name: "", username: "", age: "", height: "", weight: "" }; }
  });
  const [lastResult, setLastResult] = useState<PredictionResult | null>(() => {
    try { return JSON.parse(localStorage.getItem("medpulse-last-result") || "null"); }
    catch { return null; }
  });
  const [assessments, setAssessments] = useState<StoredAssessment[]>(() => {
    try { return JSON.parse(localStorage.getItem("medpulse-history") || "[]"); }
    catch { return []; }
  });
  const [loggedIn, setLoggedIn] = useState(() => localStorage.getItem("medpulse-session") === "1");
  const [profileCompleted, setProfileCompleted] = useState(() => localStorage.getItem("medpulse-profile-completed") === "1");
  const [mobileOpen, setMobileOpen] = useState(false);

  const navigate = (next: Page) => {
    window.location.hash = `/${next}`;
    setPage(next);
    setMobileOpen(false);
  };

  useEffect(() => {
    const onHash = () => setPage(getPath());
    window.addEventListener("hashchange", onHash);
    if (!window.location.hash) window.location.hash = "/home";
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => localStorage.setItem("medpulse-profile", JSON.stringify(profile)), [profile]);
  useEffect(() => {
    if (lastResult) localStorage.setItem("medpulse-last-result", JSON.stringify(lastResult));
  }, [lastResult]);
  useEffect(() => localStorage.setItem("medpulse-history", JSON.stringify(assessments)), [assessments]);

  const loginSuccess = async (username: string) => {
    setLoggedIn(true);
    localStorage.setItem("medpulse-session", "1");
    setProfile((p) => ({ ...p, username, name: p.name || username.split("@")[0] }));
    try {
      const result = await api.getProfile();
      setProfileCompleted(result.completed);
      localStorage.setItem("medpulse-profile-completed", result.completed ? "1" : "0");
      if (result.profile) {
        const p = result.profile as any;
        setProfile({ name: String(p.name || username), username, age: String(p.age || ""), height: String(p.height_cm || ""), weight: String(p.weight_kg || "") });
      }
      navigate(result.completed ? "dashboard" : "onboarding");
    } catch {
      navigate("onboarding");
    }
  };

  const logout = async () => {
    try { await api.logout(); } catch { /* local session still clears */ }
    setLoggedIn(false);
    localStorage.removeItem("medpulse-session");
    localStorage.removeItem("medpulse-access-token");
    navigate("home");
  };

  const guardedNavigate = (target: Page) => {
    if (["dashboard", "screening", "result", "trends", "assistant", "band", "history", "profile", "settings"].includes(target) && !loggedIn) {
      navigate("login");
      return;
    }
    navigate(target);
  };

  return (
    <div className="min-h-screen bg-[#f6f9fc] text-[#0c1a2d]">
      {page === "home" || page === "login" || page === "register" || page === "onboarding" ? (
        <>
          <PublicNav onNavigate={guardedNavigate} />
          <AnimatePresence mode="wait">
            {page === "home" && <Landing key="home" onNavigate={guardedNavigate} />}
            {page === "login" && <AuthPage mode="login" onSuccess={loginSuccess} onNavigate={navigate} />}
            {page === "register" && <AuthPage mode="register" onSuccess={loginSuccess} onNavigate={navigate} />}
            {page === "onboarding" && (
  <Onboarding
    key="onboarding"
    onComplete={(p) => {
      setProfileCompleted(true);
      localStorage.setItem("medpulse-profile-completed", "1");
      setProfile((old) => ({
        ...old,
        name: String(p.name || old.name),
        age: String(p.age || ""),
        height: String(p.height_cm || ""),
        weight: String(p.weight_kg || "")
      }));
      navigate("dashboard");
    }}
  />
)}
          </AnimatePresence>
        </>
      ) : (
        <div className="flex min-h-screen">
          <Sidebar page={page} onNavigate={guardedNavigate} onLogout={logout} mobileOpen={mobileOpen} closeMobile={() => setMobileOpen(false)} />
          <main className="min-w-0 flex-1 lg:ml-72">
            <Topbar page={page} onMenu={() => setMobileOpen(true)} onNavigate={guardedNavigate} />
            <AnimatePresence mode="wait">
              {page === "dashboard" && <Dashboard key="dashboard" profile={profile} result={lastResult} assessments={assessments} onNavigate={guardedNavigate} />}
              {page === "screening" && <Screening key="screening" onResult={(result) => {
                setLastResult(result);
                setAssessments((items) => [{ ...result, date: new Date().toISOString() }, ...items].slice(0, 50));
                navigate("result");
              }} />}
              {page === "result" && <ResultPage key="result" result={lastResult} onNavigate={guardedNavigate} />}
              {page === "trends" && <Trends key="trends" profile={profile} setProfile={setProfile} />}
              {page === "assistant" && <Assistant key="assistant" />}
              {page === "band" && <Band key="band" />}
              {page === "history" && <HistoryPage key="history" assessments={assessments} onView={(result) => { setLastResult(result); navigate("result"); }} />}
              {page === "profile" && <Profile key="profile" profile={profile} setProfile={setProfile} />}
              {page === "settings" && <SettingsPage key="settings" onLogout={logout} />}
            </AnimatePresence>
          </main>
        </div>
      )}
    </div>
  );
}

function Logo({ light = false }: { light?: boolean }) {
  return (
    <button onClick={() => navigate("home")} className="focus-ring flex items-center gap-2" aria-label="MedPulse home">
      <span className={`grid h-9 w-9 place-items-center rounded-xl ${light ? "bg-white/10 text-cyan-200" : "bg-[#0b203b] text-cyan-300"}`}>
        <HeartPulse size={20} strokeWidth={2.3} />
      </span>
      <span className={`text-lg font-black tracking-tight ${light ? "text-white" : "text-[#0b203b]"}`}>MED<span className="text-cyan-500">PULSE</span></span>
    </button>
  );
}

function PublicNav({ onNavigate }: { onNavigate: (page: Page) => void }) {
  return (
    <nav className="absolute left-0 right-0 top-0 z-40">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 lg:px-8">
        <Logo light />
        <div className="hidden items-center gap-8 text-sm font-medium text-slate-300 md:flex">
          <a href="#how" className="hover:text-white">How it works</a>
          <a href="#screenings" className="hover:text-white">Screenings</a>
          <a href="#tracking" className="hover:text-white">Tracking</a>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => onNavigate("login")} className="rounded-xl px-4 py-2 text-sm font-semibold text-white hover:bg-white/10">Log in</button>
          <button onClick={() => onNavigate("register")} className="rounded-xl bg-white px-4 py-2 text-sm font-bold text-[#0b203b] shadow-lg shadow-black/10 hover:bg-cyan-50">Create account</button>
        </div>
      </div>
    </nav>
  );
}

function Landing({ onNavigate }: { onNavigate: (page: Page) => void }) {
  return (
    <div className="mesh overflow-hidden">
      <section className="relative min-h-[760px] px-5 pb-20 pt-36 lg:px-8">
        <div className="pointer-events-none absolute left-1/2 top-20 h-96 w-96 -translate-x-1/2 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[1.02fr_.98fr]">
          <motion.div initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7 }}>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-cyan-100">
              <Sparkles size={14} /> Preventive health intelligence
            </div>
            <h1 className="max-w-3xl text-5xl font-black tracking-[-.04em] text-white sm:text-6xl lg:text-7xl">
              AI-Powered Early Disease Detection
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
              Turn everyday health data into understandable early-risk insights and track how your health changes over time.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <button onClick={() => onNavigate("login")} className="group inline-flex items-center justify-center gap-2 rounded-2xl bg-cyan-400 px-5 py-3.5 font-bold text-[#06203a] shadow-xl shadow-cyan-500/10 hover:bg-cyan-300">
                Start Health Assessment <ArrowRight size={18} className="transition group-hover:translate-x-1" />
              </button>
              <a href="#how" className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-5 py-3.5 font-semibold text-white hover:bg-white/10">
                Explore How It Works
              </a>
            </div>
            <p className="mt-5 text-xs text-slate-400">ML-based screening • Risk estimate • Not a medical diagnosis</p>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: .8, delay: .1 }}>
            <HeroVisual />
          </motion.div>
        </div>
      </section>

      <section id="how" className="bg-[#f6f9fc] px-5 py-24 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <SectionHeading eyebrow="How it works" title="From health data to an early-risk picture." text="A simple flow connects user-friendly inputs with disease-specific machine learning, then turns the output into something a person can actually understand." />
          <div className="mt-12 grid gap-4 md:grid-cols-5">
            {([
              ["01", "HEALTH DATA", Activity], ["02", "DISEASE-SPECIFIC ML", BrainCircuit], ["03", "RISK ESTIMATION", Gauge],
              ["04", "AI EXPLANATION", MessageCircle], ["05", "PREVENTIVE INSIGHTS", Leaf]
            ] as const).map(([num, title, Icon], i) => (
              <motion.div key={String(num)} initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * .06 }} className="glass rounded-3xl p-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-cyan-600">{num}</span>
                  <Icon size={19} className="text-slate-500" />
                </div>
                <div className="mt-10 text-sm font-extrabold tracking-wide text-slate-800">{String(title)}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-white px-5 py-24 lg:px-8">
        <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[.8fr_1.2fr] lg:items-center">
          <SectionHeading eyebrow="Why MedPulse" title="Not another dashboard full of numbers." text="MedPulse is designed around one idea: turn health data into an understandable early-risk picture and show how that picture changes over time." />
          <div className="grid gap-4 sm:grid-cols-2">
            {([
              ["Early Risk Screening", "Disease-specific ML estimates potential risk before a user sees a confirmed diagnosis.", Gauge],
              ["Continuous Health Tracking", "Keep a longitudinal view of measurements instead of treating health as a one-time check.", BarChart3],
              ["Disease-Specific ML", "Each screening connects to the model and feature schema already exposed by your FastAPI backend.", BrainCircuit],
              ["Simple User Inputs", "Translate technical model fields into understandable questions without changing the payload the model receives.", User],
              ["AI-Powered Explanation", "ML predicts; an AI layer can explain the result without pretending to diagnose.", Sparkles],
              ["Future Wearable Integration", "A future MedPulse Band can feed continuous physiological data into the same longitudinal platform.", Watch],
            ] as const).map(([title, text, Icon]) => (
              <div key={String(title)} className="rounded-3xl border border-slate-200 bg-slate-50/70 p-5">
                <div className="mb-4 grid h-10 w-10 place-items-center rounded-xl bg-white text-cyan-600 shadow-sm"><Icon size={19} /></div>
                <h3 className="font-bold">{String(title)}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{String(text)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="screenings" className="bg-[#f6f9fc] px-5 py-24 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <SectionHeading eyebrow="10 screenings" title="Disease-specific screening, one calm interface." text="Every card maps to a real FastAPI prediction route and schema in the current MedPulse backend." />
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {diseases.map((disease) => <DiseaseCard key={disease.id} disease={disease} onAssess={() => onNavigate("login")} />)}
          </div>
        </div>
      </section>

      <section id="tracking" className="bg-white px-5 py-24 lg:px-8">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[.85fr_1.15fr] lg:items-center">
          <div>
            <SectionHeading eyebrow="Longitudinal health" title="Don't just check your health once. Track how it changes." text="Monthly measurements can become a context layer around future screening results. The prototype stores this tracking data locally until a dedicated health-data endpoint is connected." />
            <div className="mt-8 flex flex-wrap gap-2">
              {["Weight", "BMI", "Blood Pressure", "Heart Rate"].map((m) => <span key={m} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-slate-600">{m}</span>)}
            </div>
          </div>
          <TrackingPreview />
        </div>
      </section>

      <footer className="mesh border-t border-white/10 px-5 py-12 text-slate-300 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 sm:flex-row sm:items-center">
          <div><Logo light /><p className="mt-3 text-xs text-slate-400">Understand your health. Track your risks. Act earlier.</p></div>
          <p className="max-w-md text-right text-xs leading-5 text-slate-400">MedPulse screening estimates are generated using machine-learning models and are not medical diagnoses.</p>
        </div>
      </footer>
    </div>
  );
}

function HeroVisual() {
  return (
    <div className="relative mx-auto max-w-xl">
      <div className="pulse-ring absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/20" />
      <div className="dark-glass relative rounded-[2rem] p-5 shadow-2xl shadow-black/20">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div><div className="text-xs font-semibold text-slate-400">MEDPULSE / OVERVIEW</div><div className="mt-1 font-bold text-white">Health journey</div></div>
          <span className="flex items-center gap-1.5 rounded-full bg-emerald-400/10 px-2.5 py-1 text-[10px] font-bold text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-300" /> SYSTEM READY</span>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-3">
          {([
            ["Risk Score", "—", "No assessment yet", Gauge],
            ["BMI", "—", "Calculated from height + weight", Scale],
            ["Heart Rate", "—", "Wearable integration ready", HeartPulse],
            ["Health Trend", "—", "History starts with your data", BarChart3],
          ] as const).map(([title, value, note, Icon]) => (
            <div key={String(title)} className="rounded-2xl border border-white/10 bg-white/[.045] p-4">
              <Icon size={17} className="text-cyan-300" />
              <div className="mt-5 text-xs text-slate-400">{String(title)}</div>
              <div className="mt-1 text-2xl font-black text-white">{String(value)}</div>
              <div className="mt-1 text-[10px] leading-4 text-slate-500">{String(note)}</div>
            </div>
          ))}
        </div>
        <div className="mt-3 rounded-2xl border border-white/10 bg-white/[.045] p-4">
          <div className="flex items-center justify-between text-xs"><span className="font-semibold text-slate-300">Disease screening</span><span className="text-slate-500">10 models available</span></div>
          <div className="mt-3 flex gap-1.5">{Array.from({ length: 10 }).map((_, i) => <span key={i} className="h-1.5 flex-1 rounded-full bg-cyan-400/35" />)}</div>
        </div>
      </div>
    </div>
  );
}

function TrackingPreview() {
  const data = [
    { month: "M1", weight: null, bmi: null },
    { month: "M2", weight: null, bmi: null },
    { month: "M3", weight: null, bmi: null },
    { month: "M4", weight: null, bmi: null },
  ];
  return (
    <div className="glass rounded-[2rem] p-5">
      <div className="flex items-center justify-between"><div><p className="text-xs font-bold text-cyan-600">MONTHLY TRACKING</p><h3 className="mt-1 font-bold">Your trend starts with your measurements.</h3></div><CalendarDays size={20} className="text-slate-400" /></div>
      <div className="mt-6 h-52">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}><CartesianGrid stroke="#e7eef5" strokeDasharray="3 3" /><XAxis dataKey="month" tick={{ fontSize: 11 }} /><YAxis hide /><Tooltip /><Line type="monotone" dataKey="weight" stroke="#0ea5e9" strokeWidth={2.5} dot={false} connectNulls={false} /></LineChart>
        </ResponsiveContainer>
      </div>
      <div className="rounded-2xl bg-slate-50 p-3 text-xs text-slate-500"><Info size={14} className="mr-2 inline text-cyan-600" /> No measurements are fabricated in this preview.</div>
    </div>
  );
}

function SectionHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  return <div className="max-w-2xl"><div className="text-xs font-black uppercase tracking-[.18em] text-cyan-600">{eyebrow}</div><h2 className="mt-3 text-3xl font-black tracking-tight text-[#0b203b] sm:text-4xl">{title}</h2><p className="mt-4 leading-7 text-slate-500">{text}</p></div>;
}

function DiseaseCard({ disease, onAssess }: { disease: typeof diseases[number]; onAssess: () => void }) {
  const Icon = disease.icon;
  return <div className="group rounded-3xl border border-slate-200 bg-white p-5 transition hover:-translate-y-1 hover:border-cyan-200 hover:shadow-xl hover:shadow-slate-200/50">
    <div className="grid h-11 w-11 place-items-center rounded-2xl bg-cyan-50 text-cyan-600"><Icon size={20} /></div>
    <h3 className="mt-5 font-bold text-slate-800">{disease.name}</h3>
    <p className="mt-2 min-h-10 text-xs leading-5 text-slate-500">{disease.blurb}</p>
    <button onClick={onAssess} className="mt-5 flex items-center gap-1 text-xs font-bold text-cyan-700 group-hover:gap-2">Assess Risk <ChevronRight size={14} /></button>
  </div>;
}

function Onboarding({ onComplete }: { onComplete: (profile: any) => void }) {
  const [step, setStep] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [data, setData] = useState<any>({
    name: "",
    date_of_birth: "",
    age: "",
    gender: "",
    height_cm: "",
    weight_kg: "",
    blood_pressure: "",
    resting_heart_rate: "",
    spo2: "",
    activity_level: "",
    exercise_frequency: "",
    smoking: "",
    alcohol: "",
    sleep_hours: "",
    sleep_quality: "",
    water_intake_liters: "",
    existing_conditions: "",
    medications: "",
    allergies: "",
    family_history: "",
    goals: [],
  });

  const update = (key: string, value: any) =>
    setData((p: any) => ({ ...p, [key]: value }));

  const bmi =
    data.height_cm && data.weight_kg
      ? Number(
          Number(data.weight_kg) /
            Math.pow(Number(data.height_cm) / 100, 2)
        ).toFixed(1)
      : "";

  const toggleGoal = (goal: string) => {
    setData((p: any) => ({
      ...p,
      goals: p.goals.includes(goal)
        ? p.goals.filter((x: string) => x !== goal)
        : [...p.goals, goal],
    }));
  };

  const next = () => {
    setError("");
    if (step === 1 && !data.name.trim()) {
      setError("Please enter your name.");
      return;
    }
    if (step === 2 && (!data.height_cm || !data.weight_kg)) {
      setError("Height and weight are required.");
      return;
    }
    setStep((s) => Math.min(5, s + 1));
  };

  const submit = async () => {
    setBusy(true);
    setError("");

    try {
      const payload = {
        ...data,
        age: data.age ? Number(data.age) : null,
        height_cm: data.height_cm ? Number(data.height_cm) : null,
        weight_kg: data.weight_kg ? Number(data.weight_kg) : null,
        resting_heart_rate: data.resting_heart_rate ? Number(data.resting_heart_rate) : null,
        spo2: data.spo2 ? Number(data.spo2) : null,
        sleep_hours: data.sleep_hours ? Number(data.sleep_hours) : null,
        water_intake_liters: data.water_intake_liters ? Number(data.water_intake_liters) : null,
      };

      const result = await api.saveProfile(payload);

      localStorage.setItem("medpulse-profile-completed", "1");

      onComplete(result.profile);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.detail || err.message
          : "Unable to save your health profile."
      );
    } finally {
      setBusy(false);
    }
  };

  const inputClass =
    "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-400";

  return (
    <motion.main
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-screen bg-[#f6f9fc] px-5 py-10 lg:px-8"
    >
      <div className="mx-auto max-w-3xl">
        <div className="mb-8">
          <div className="text-xs font-black uppercase tracking-[.18em] text-cyan-600">
            MEDPULSE
          </div>
          <h1 className="mt-2 text-4xl font-black text-[#0b203b]">
            Complete your health profile
          </h1>
          <p className="mt-3 text-slate-500">
            This creates your personal baseline for preventive health tracking.
          </p>
        </div>

        <div className="mb-8 grid grid-cols-5 gap-2">
          {["Basics", "Body", "Vitals", "Lifestyle", "Goals"].map((label, i) => (
            <div key={label}>
              <div
                className={`h-1.5 rounded-full ${
                  i + 1 <= step ? "bg-cyan-500" : "bg-slate-200"
                }`}
              />
              <span className="mt-2 block text-[10px] font-bold text-slate-500">
                {label}
              </span>
            </div>
          ))}
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/40 sm:p-9">
          {step === 1 && (
            <div className="space-y-5">
              <SectionHeading
                eyebrow="01"
                title="Tell us about yourself"
                text="Basic information helps personalize your MedPulse experience."
              />

              <Field label="Full name" value={data.name} onChange={(v) => update("name", v)} required />
              <Field label="Date of birth" value={data.date_of_birth} onChange={(v) => update("date_of_birth", v)} type="date" />

              <div>
                <label className="mb-1.5 block text-xs font-semibold text-slate-700">Age</label>
                <input className={inputClass} type="number" min="1" max="120" value={data.age} onChange={(e) => update("age", e.target.value)} />
              </div>

              <div>
                <label className="mb-1.5 block text-xs font-semibold text-slate-700">Gender</label>
                <select className={inputClass} value={data.gender} onChange={(e) => update("gender", e.target.value)}>
                  <option value="">Prefer not to say</option>
                  <option>Female</option>
                  <option>Male</option>
                  <option>Non-binary</option>
                  <option>Other</option>
                </select>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <SectionHeading
                eyebrow="02"
                title="Your body measurements"
                text="We calculate BMI automatically from your height and weight."
              />

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-xs font-semibold text-slate-700">Height (cm)</label>
                  <input className={inputClass} type="number" value={data.height_cm} onChange={(e) => update("height_cm", e.target.value)} />
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-semibold text-slate-700">Weight (kg)</label>
                  <input className={inputClass} type="number" value={data.weight_kg} onChange={(e) => update("weight_kg", e.target.value)} />
                </div>
              </div>

              {bmi && (
                <div className="rounded-2xl bg-cyan-50 p-5">
                  <div className="text-xs font-bold uppercase tracking-wider text-cyan-700">Calculated BMI</div>
                  <div className="mt-1 text-4xl font-black text-[#0b203b]">{bmi}</div>
                  <div className="mt-1 text-xs text-slate-500">
                    Calculated from your height and weight.
                  </div>
                </div>
              )}
            </div>
          )}

          {step === 3 && (
            <div className="space-y-5">
              <SectionHeading
                eyebrow="03"
                title="Your current measurements"
                text="Only provide measurements you actually know. We never invent missing values."
              />

              <div className="grid gap-5 sm:grid-cols-3">
                <div>
                  <label className="mb-1.5 block text-xs font-semibold text-slate-700">Blood pressure</label>
                  <input className={inputClass} placeholder="120/80" value={data.blood_pressure} onChange={(e) => update("blood_pressure", e.target.value)} />
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-semibold text-slate-700">Resting heart rate</label>
                  <input className={inputClass} type="number" placeholder="Optional" value={data.resting_heart_rate} onChange={(e) => update("resting_heart_rate", e.target.value)} />
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-semibold text-slate-700">SpO₂ (%)</label>
                  <input className={inputClass} type="number" placeholder="Optional" value={data.spo2} onChange={(e) => update("spo2", e.target.value)} />
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-5">
              <SectionHeading
                eyebrow="04"
                title="Your lifestyle"
                text="These details help build a useful longitudinal health baseline."
              />

              <div className="grid gap-5 sm:grid-cols-2">
                <select className={inputClass} value={data.activity_level} onChange={(e) => update("activity_level", e.target.value)}>
                  <option value="">Activity level</option>
                  <option>Sedentary</option>
                  <option>Lightly active</option>
                  <option>Moderately active</option>
                  <option>Very active</option>
                </select>

                <select className={inputClass} value={data.exercise_frequency} onChange={(e) => update("exercise_frequency", e.target.value)}>
                  <option value="">Exercise frequency</option>
                  <option>Never</option>
                  <option>1–2 times/week</option>
                  <option>3–4 times/week</option>
                  <option>5+ times/week</option>
                </select>

                <select className={inputClass} value={data.smoking} onChange={(e) => update("smoking", e.target.value)}>
                  <option value="">Smoking</option>
                  <option>Never</option>
                  <option>Former smoker</option>
                  <option>Current smoker</option>
                </select>

                <select className={inputClass} value={data.alcohol} onChange={(e) => update("alcohol", e.target.value)}>
                  <option value="">Alcohol consumption</option>
                  <option>Never</option>
                  <option>Occasionally</option>
                  <option>Regularly</option>
                </select>

                <input className={inputClass} type="number" step="0.5" placeholder="Sleep hours" value={data.sleep_hours} onChange={(e) => update("sleep_hours", e.target.value)} />

                <select className={inputClass} value={data.sleep_quality} onChange={(e) => update("sleep_quality", e.target.value)}>
                  <option value="">Sleep quality</option>
                  <option>Excellent</option>
                  <option>Good</option>
                  <option>Average</option>
                  <option>Poor</option>
                </select>
              </div>

              <textarea className={inputClass} rows={3} placeholder="Existing medical conditions (optional)" value={data.existing_conditions} onChange={(e) => update("existing_conditions", e.target.value)} />
              <textarea className={inputClass} rows={3} placeholder="Current medications (optional)" value={data.medications} onChange={(e) => update("medications", e.target.value)} />
              <textarea className={inputClass} rows={3} placeholder="Allergies (optional)" value={data.allergies} onChange={(e) => update("allergies", e.target.value)} />
              <textarea className={inputClass} rows={3} placeholder="Family health history (optional)" value={data.family_history} onChange={(e) => update("family_history", e.target.value)} />
            </div>
          )}

          {step === 5 && (
            <div className="space-y-5">
              <SectionHeading
                eyebrow="05"
                title="What are your goals?"
                text="Choose what you want MedPulse to help you track."
              />

              <div className="grid gap-3 sm:grid-cols-2">
                {[
                  "Understand my health risks",
                  "Track my health",
                  "Improve fitness",
                  "Manage weight",
                  "Monitor existing conditions",
                  "General preventive health",
                ].map((goal) => (
                  <button
                    type="button"
                    key={goal}
                    onClick={() => toggleGoal(goal)}
                    className={`rounded-2xl border p-4 text-left text-sm font-semibold ${
                      data.goals.includes(goal)
                        ? "border-cyan-400 bg-cyan-50 text-cyan-800"
                        : "border-slate-200 bg-white text-slate-600"
                    }`}
                  >
                    {goal}
                  </button>
                ))}
              </div>

              <div className="rounded-2xl bg-slate-50 p-4 text-xs leading-5 text-slate-500">
                Your screening estimates are generated using machine-learning
                models and are not medical diagnoses.
              </div>
            </div>
          )}

          {error && (
            <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="mt-8 flex justify-between gap-3">
            <button
              type="button"
              disabled={step === 1 || busy}
              onClick={() => setStep((s) => Math.max(1, s - 1))}
              className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-600 disabled:opacity-30"
            >
              Back
            </button>

            {step < 5 ? (
              <button
                type="button"
                onClick={next}
                className="rounded-xl bg-[#0b203b] px-6 py-3 text-sm font-bold text-white"
              >
                Continue
              </button>
            ) : (
              <button
                type="button"
                disabled={busy}
                onClick={submit}
                className="rounded-xl bg-cyan-500 px-6 py-3 text-sm font-bold text-white disabled:opacity-50"
              >
                {busy ? "Saving..." : "Complete profile"}
              </button>
            )}
          </div>
        </div>

        <p className="mt-5 text-center text-xs text-slate-400">
          MedPulse uses your information to provide preventive health insights.
          It does not provide confirmed medical diagnoses.
        </p>
      </div>
    </motion.main>
  );
}
function AuthPage({ mode, onSuccess, onNavigate }: { mode: "login" | "register"; onSuccess: (username: string) => void; onNavigate: (page: Page) => void }) {
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setError("");
    if (mode === "register" && password !== confirm) { setError("Passwords do not match."); return; }
    setBusy(true);
    try {
      if (mode === "login") {
        const loginResult = await api.login(username, password);
        localStorage.setItem("medpulse-access-token", loginResult.access_token);
      }
      else {
        await api.register(username, password);
        const loginResult = await api.login(username, password);
        localStorage.setItem("medpulse-access-token", loginResult.access_token);
      }
      if (mode === "register" && name.trim()) localStorage.setItem("medpulse-profile", JSON.stringify({ name: name.trim(), username, age: "", height: "", weight: "" }));
      onSuccess(username);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail || err.message : "Something went wrong.");
    } finally { setBusy(false); }
  };

  return <motion.main initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mesh grid min-h-screen place-items-center px-5 py-28">
    <div className="w-full max-w-md">
      <div className="mb-8"><Logo light /></div>
      <div className="rounded-[2rem] border border-white/10 bg-white/[.07] p-6 shadow-2xl backdrop-blur-xl sm:p-8">
        <div className="mb-7"><div className="mb-3 grid h-11 w-11 place-items-center rounded-2xl bg-cyan-400/15 text-cyan-200">{mode === "login" ? <LogIn size={20} /> : <UserPlus size={20} />}</div><h1 className="text-3xl font-black text-white">{mode === "login" ? "Welcome back" : "Create your account"}</h1><p className="mt-2 text-sm text-slate-400">{mode === "login" ? "Continue your health journey." : "Create a patient account for your MedPulse prototype."}</p></div>
        <form onSubmit={submit} className="space-y-4">
          {mode === "register" && <Field dark label="Name" value={name} onChange={setName} placeholder="Your name" />}
          <Field dark label="Email / username" value={username} onChange={setUsername} placeholder="you@example.com" type="text" required />
          <Field dark label="Password" value={password} onChange={setPassword} placeholder="At least 12 characters" type="password" required />
          {mode === "register" && <Field dark label="Confirm password" value={confirm} onChange={setConfirm} placeholder="Repeat password" type="password" required />}
          {error && <div className="rounded-xl border border-red-300/20 bg-red-400/10 p-3 text-xs leading-5 text-red-200"><AlertCircle size={14} className="mr-1 inline" />{error}</div>}
          <button disabled={busy} className="flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-3.5 font-bold text-[#06203a] disabled:cursor-wait disabled:opacity-60">{busy ? <RefreshCw size={17} className="animate-spin" /> : mode === "login" ? "Log in" : "Create account"} {!busy && <ArrowRight size={17} />}</button>
        </form>
        <div className="mt-6 flex items-center justify-between text-xs text-slate-400">
          <button onClick={() => onNavigate(mode === "login" ? "register" : "login")} className="font-semibold text-cyan-300 hover:text-cyan-200">{mode === "login" ? "Create Account" : "Already have an account? Log in"}</button>
          {mode === "login" && <span>Forgot password</span>}
        </div>
        <p className="mt-6 border-t border-white/10 pt-5 text-[11px] leading-5 text-slate-500">Authentication uses the existing FastAPI /auth endpoints. Health data remains sensitive; use secure deployment settings before production.</p>
      </div>
    </div>
  </motion.main>;
}

function Field({ label, value, onChange, placeholder, type = "text", required = false, dark = false }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string; required?: boolean; dark?: boolean }) {
  return <label className="block"><span className={`mb-1.5 block text-xs font-semibold ${dark ? "text-slate-300" : "text-slate-700"}`}>{label}</span><input required={required} type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={`focus-ring w-full rounded-xl border px-3.5 py-3 text-sm outline-none ${dark ? "border-white/10 bg-white/[.06] text-white placeholder:text-slate-600 focus:border-cyan-300/50" : "border-slate-200 bg-white text-slate-800 placeholder:text-slate-400 focus:border-cyan-400"}`} /></label>;
}

function Sidebar({ page, onNavigate, onLogout, mobileOpen, closeMobile }: { page: Page; onNavigate: (p: Page) => void; onLogout: () => void; mobileOpen: boolean; closeMobile: () => void }) {
  const items: [Page, string, typeof House][] = [
    ["dashboard", "Dashboard", House], ["screening", "Health Assessment", FileHeart], ["trends", "Health Trends", BarChart3],
    ["assistant", "AI Assistant", MessageCircle], ["band", "MedPulse Band", Watch], ["history", "History", History],
    ["profile", "Profile", User], ["settings", "Settings", Settings],
  ];
  return <>
    {mobileOpen && <button aria-label="Close navigation" onClick={closeMobile} className="fixed inset-0 z-50 bg-slate-950/40 lg:hidden" />}
    <aside className={`fixed inset-y-0 left-0 z-50 w-72 border-r border-slate-200 bg-white transition-transform lg:translate-x-0 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
      <div className="flex h-full flex-col p-5">
        <div className="flex items-center justify-between"><Logo /><button onClick={closeMobile} className="rounded-lg p-2 text-slate-400 lg:hidden"><X size={18} /></button></div>
        <div className="mt-8 rounded-2xl bg-[#f1f7fb] p-3"><div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-white text-cyan-600 shadow-sm"><HeartPulse size={18} /></div><div><p className="text-xs font-bold text-slate-800">MEDPULSE</p><p className="text-[10px] text-slate-500">Preventive health</p></div></div></div>
        <nav className="mt-6 flex-1 space-y-1">
          {items.map(([id, label, Icon]) => <button key={id} onClick={() => { onNavigate(id); closeMobile(); }} className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-semibold transition ${page === id ? "bg-[#0b203b] text-white shadow-lg shadow-slate-900/10" : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"}`}><Icon size={17} />{label}</button>)}
        </nav>
        <div className="rounded-2xl border border-cyan-100 bg-cyan-50/70 p-4"><div className="flex items-center gap-2 text-xs font-bold text-cyan-800"><ShieldCheck size={15} /> Privacy-first prototype</div><p className="mt-2 text-[10px] leading-4 text-cyan-900/60">No regulatory compliance claims are made by this prototype.</p></div>
        <button onClick={onLogout} className="mt-3 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-500 hover:bg-red-50 hover:text-red-600"><LogOut size={17} /> Log out</button>
      </div>
    </aside>
  </>;
}

function Topbar({ page, onMenu, onNavigate }: { page: Page; onMenu: () => void; onNavigate: (p: Page) => void }) {
  const title = page === "dashboard" ? "Dashboard" : page === "screening" ? "Health Assessment" : page === "result" ? "Screening Result" : page === "trends" ? "Health Trends" : page === "assistant" ? "AI Assistant" : page === "band" ? "MedPulse Band" : page[0].toUpperCase() + page.slice(1);
  return <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200 bg-white/85 px-5 backdrop-blur-xl lg:px-8">
    <div className="flex items-center gap-3"><button onClick={onMenu} className="rounded-xl border border-slate-200 p-2 text-slate-500 lg:hidden"><Menu size={18} /></button><div><p className="text-xs font-semibold text-slate-400">MEDPULSE</p><h1 className="font-black tracking-tight">{title}</h1></div></div>
    <div className="flex items-center gap-2"><button onClick={() => onNavigate("screening")} className="hidden items-center gap-2 rounded-xl bg-[#0b203b] px-3.5 py-2.5 text-xs font-bold text-white sm:flex"><Plus size={15} /> New Assessment</button><button className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-slate-500"><Bell size={17} /></button></div>
  </header>;
}

function Shell({ children, title, subtitle }: { children: React.ReactNode; title: string; subtitle: string }) {
  return <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-10"><div className="mb-8"><p className="text-xs font-black uppercase tracking-[.16em] text-cyan-600">MEDPULSE</p><h2 className="mt-2 text-3xl font-black tracking-tight text-[#0b203b]">{title}</h2><p className="mt-2 text-sm text-slate-500">{subtitle}</p></div>{children}</motion.div>;
}

function Dashboard({ profile, result, assessments, onNavigate }: { profile: UserProfile; result: PredictionResult | null; assessments: StoredAssessment[]; onNavigate: (p: Page) => void }) {
  const bmi = profile.height && profile.weight ? Number(profile.weight) / Math.pow(Number(profile.height) / 100, 2) : null;
  return <Shell title={`Good morning${profile.name ? `, ${profile.name.split(" ")[0]}` : ""}.`} subtitle="Your health journey at a glance.">
    <div className="grid gap-4 lg:grid-cols-4">
      <RiskCard result={result} />
      <MetricCard title="Latest Assessment" value={result?.disease || "—"} note={result ? new Date(assessments[0]?.date || Date.now()).toLocaleDateString() : "No assessment yet"} icon={FileHeart} />
      <MetricCard title="BMI" value={bmi ? bmi.toFixed(1) : "—"} note={bmi ? "Calculated from height + weight" : "Add height and weight"} icon={Scale} />
      <MetricCard title="Wearable Status" value="Coming Soon" note="No live readings are shown" icon={Watch} />
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-[1.35fr_.65fr]">
      <div className="glass rounded-3xl p-5">
        <div className="flex items-center justify-between"><div><p className="text-xs font-bold text-cyan-600">RISK OVERVIEW</p><h3 className="mt-1 font-bold">Your latest screening</h3></div><button onClick={() => onNavigate("screening")} className="text-xs font-bold text-cyan-700">New assessment â†’</button></div>
        <div className="mt-6 grid gap-6 md:grid-cols-[220px_1fr] md:items-center">{result ? <RiskGauge score={result.risk_score} level={result.risk_level} /> : <EmptyGauge />}{result ? <div><div className="text-sm font-semibold text-slate-500">{result.disease}</div><div className="mt-1 text-3xl font-black text-[#0b203b]">{formatPercent(result.probability)} probability</div><p className="mt-3 max-w-lg text-sm leading-6 text-slate-500">This is an ML-based screening estimate, not a confirmed diagnosis. Review the full result for the model response and disclaimer.</p><button onClick={() => onNavigate("result")} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-100 px-3.5 py-2.5 text-xs font-bold text-slate-700">View result <ArrowRight size={14} /></button></div> : <div><h3 className="text-xl font-black">No screening result yet</h3><p className="mt-2 text-sm leading-6 text-slate-500">Start an assessment to populate this dashboard with a real backend result.</p><button onClick={() => onNavigate("screening")} className="mt-5 rounded-xl bg-[#0b203b] px-4 py-2.5 text-xs font-bold text-white">Start screening</button></div>}</div>
      </div>
      <div className="rounded-3xl bg-[#0b203b] p-5 text-white"><div className="flex items-center gap-2 text-xs font-bold text-cyan-300"><Sparkles size={15} /> MEDPULSE DIFFERENTIATOR</div><h3 className="mt-5 text-xl font-black leading-7">Numbers become a risk story.</h3><p className="mt-3 text-sm leading-6 text-slate-300">We don't just show health numbers — we turn health data into an understandable early-risk picture and track how that risk changes over time.</p><button onClick={() => onNavigate("trends")} className="mt-6 flex items-center gap-2 text-xs font-bold text-cyan-300">Explore trends <ArrowRight size={14} /></button></div>
    </div>
    <div className="mt-5"><div className="mb-4 flex items-end justify-between"><div><p className="text-xs font-bold text-cyan-600">SUPPORTED SCREENINGS</p><h3 className="mt-1 text-xl font-black">10 disease-specific models</h3></div><button onClick={() => onNavigate("screening")} className="text-xs font-bold text-slate-500 hover:text-slate-800">View all</button></div><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{diseases.map((d) => <button key={d.id} onClick={() => onNavigate("screening")} className="rounded-2xl border border-slate-200 bg-white p-4 text-left hover:border-cyan-200 hover:shadow-lg"><div className="flex items-center justify-between"><d.icon size={18} className="text-cyan-600" /><ChevronRight size={15} className="text-slate-300" /></div><div className="mt-4 text-sm font-bold">{d.name}</div></button>)}</div></div>
  </Shell>;
}

function MetricCard({ title, value, note, icon: Icon }: { title: string; value: string; note: string; icon: typeof Activity }) {
  return <div className="rounded-3xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between"><span className="text-xs font-semibold text-slate-400">{title}</span><span className="grid h-9 w-9 place-items-center rounded-xl bg-slate-50 text-cyan-600"><Icon size={17} /></span></div><div className="mt-6 truncate text-2xl font-black text-[#0b203b]">{value}</div><div className="mt-1 text-[11px] text-slate-400">{note}</div></div>;
}

function RiskCard({ result }: { result: PredictionResult | null }) {
  return <div className="rounded-3xl bg-[#0b203b] p-5 text-white"><div className="flex items-center justify-between"><span className="text-xs font-semibold text-slate-400">Overall Risk</span><Gauge size={18} className="text-cyan-300" /></div><div className="mt-6 text-4xl font-black">{result ? `${result.risk_score}/100` : "—"}</div><div className="mt-1 text-xs text-slate-400">{result ? capitalize(result.risk_level) : "Awaiting screening"}</div></div>;
}

function EmptyGauge() { return <div className="relative mx-auto grid h-48 w-48 place-items-center rounded-full border-[18px] border-slate-100"><div className="text-center"><div className="text-3xl font-black">—</div><div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">No result</div></div></div>; }

function RiskGauge({ score, level }: { score: number; level: string }) {
  const deg = Math.max(0, Math.min(180, score * 1.8));
  return <div className="mx-auto"><div className="relative h-28 w-56 overflow-hidden"><div className="absolute bottom-0 h-56 w-56 rounded-full border-[18px] border-slate-100" /><div className="absolute bottom-0 h-56 w-56 rounded-full border-[18px] border-cyan-500" style={{ clipPath: `polygon(0 0, ${Math.min(100, deg / 1.8)}% 0, ${Math.min(100, deg / 1.8)}% 100%, 0 100%)` }} /><div className="absolute bottom-0 left-1/2 h-1 w-24 origin-left -translate-y-2 rounded-full bg-[#0b203b]" style={{ transform: `rotate(${deg - 90}deg)`, transformOrigin: "0 50%" }} /></div><div className="-mt-1 text-center"><div className="text-4xl font-black">{score}</div><div className="text-xs font-bold uppercase tracking-wider text-slate-400">{capitalize(level)}</div></div></div>;
}

function Screening({ onResult }: { onResult: (result: PredictionResult) => void }) {
  const [disease, setDisease] = useState(diseases[0].id);
  const [schema, setSchema] = useState<DiseaseSchema | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [simpleAnswers, setSimpleAnswers] = useState<Record<string, unknown>>({});
  const [reportFiles, setReportFiles] = useState<Record<string, File | null>>({});
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const selected = diseases.find((d) => d.id === disease)!;

  useEffect(() => {
    let active = true;
    setLoadingSchema(true); setError(""); setSchema(null); setValues({});
    api.getDiseaseSchema(disease).then((data) => { if (active) setSchema(data); }).catch((e) => { if (active) setError(e instanceof ApiError ? e.detail || e.message : "Could not load the disease schema."); }).finally(() => { if (active) setLoadingSchema(false); });
    return () => { active = false; };
  }, [disease]);

  const bmiFields = schema?.features.filter((f) => f.toLowerCase() === "bmi") ?? [];
  const hasHeightWeight = schema?.features.some((f) => f.toLowerCase() === "height") && schema?.features.some((f) => f.toLowerCase() === "weight");
  const bmi = hasHeightWeight && values.height && values.weight ? Number(values.weight) / Math.pow(Number(values.height) / 100, 2) : null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setError("");
    if (!schema) return;
    const payload: Record<string, unknown> = {};
    for (const feature of schema.features) {
      let value = values[feature];
      if (feature.toLowerCase() === "bmi" && !value && bmi) value = bmi.toFixed(2);
      if (value === undefined || value === "") { setError(`Please provide "${labelFor(feature)}".`); return; }
      const numeric = Number(value);
      payload[feature] = value.trim() !== "" && Number.isFinite(numeric) ? numeric : value.trim();
    }
    setSubmitting(true);
    try { const result = await api.predictDisease(disease, payload); onResult(result); }
    catch (e) { setError(e instanceof ApiError ? e.detail || e.message : "The screening request failed."); }
    finally { setSubmitting(false); }
  };

  return <Shell title="Disease Screening" subtitle="Choose a disease, fetch its real backend schema, and submit only the information required by that model.">
    <div className="grid gap-6 lg:grid-cols-[290px_1fr]">
      <div className="space-y-2 rounded-3xl border border-slate-200 bg-white p-3">
        <div className="px-3 pb-2 pt-1 text-xs font-black uppercase tracking-wider text-slate-400">Choose screening</div>
        {diseases.map((d) => <button key={d.id} onClick={() => setDisease(d.id)} className={`flex w-full items-center gap-3 rounded-2xl p-3 text-left ${d.id === disease ? "bg-[#0b203b] text-white" : "hover:bg-slate-50"}`}><d.icon size={17} className={d.id === disease ? "text-cyan-300" : "text-cyan-600"} /><span className="text-sm font-bold">{d.name}</span></button>)}
      </div>
      <div className="glass rounded-3xl p-5 sm:p-7">
        <div className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between"><div><p className="text-xs font-black uppercase tracking-wider text-cyan-600">REAL API SCHEMA</p><h3 className="mt-1 text-2xl font-black">{selected.name}</h3><p className="mt-1 text-sm text-slate-500">Fields are loaded from <code>/predict/{disease}/schema</code>.</p></div><div className="rounded-xl bg-slate-100 px-3 py-2 text-xs font-bold text-slate-600">{schema?.feature_count ?? "—"} features</div></div>
        {loadingSchema ? <div className="grid min-h-80 place-items-center"><RefreshCw className="animate-spin text-cyan-600" /></div> : error && !schema ? <ErrorPanel message={error} onRetry={() => setDisease(disease)} /> : schema ? <form onSubmit={submit} className="mt-6"><div className="grid gap-4 md:grid-cols-2">{schema.features.map((feature) => <FeatureInput key={feature} feature={feature} value={values[feature] ?? ""} onChange={(v) => setValues((x) => ({ ...x, [feature]: v }))} />)}</div>{hasHeightWeight && bmi && <div className="mt-4 rounded-2xl border border-cyan-100 bg-cyan-50 p-4 text-sm"><Scale size={17} className="mr-2 inline text-cyan-600" /> Calculated BMI: <strong>{bmi.toFixed(1)}</strong>. This is derived from height + weight; it is not fabricated.</div>}{bmiFields.length > 0 && !hasHeightWeight && <div className="mt-4 rounded-2xl border border-amber-100 bg-amber-50 p-4 text-xs leading-5 text-amber-800"><Info size={14} className="mr-2 inline" /> This model explicitly expects BMI. Enter the value if you have it; MedPulse will not invent one.</div>}{error && <div className="mt-4"><ErrorPanel message={error} /></div>}<div className="mt-6 flex flex-col justify-between gap-4 border-t border-slate-200 pt-5 sm:flex-row sm:items-center"><p className="text-[11px] leading-5 text-slate-400">Your submission goes directly to the existing FastAPI disease route. No prediction is generated in the frontend.</p><button disabled={submitting} className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#0b203b] px-5 py-3 font-bold text-white disabled:opacity-60">{submitting ? <RefreshCw size={17} className="animate-spin" /> : <Zap size={17} />} {submitting ? "Screening…" : "Run ML Screening"}</button></div></form> : null}
      </div>
    </div>
  </Shell>;
}


function buildScreeningPayload(
  disease: string,
  answers: Record<string, unknown>,
  profile: { age?: string | number; height?: string | number; weight?: string | number }
): Record<string, unknown> {
  const payload: Record<string, unknown> = { ...answers };

  // Existing profile information is reused automatically.
  if (profile.age) payload.age = Number(profile.age);
  if (profile.height) payload.height = Number(profile.height);
  if (profile.weight) payload.weight = Number(profile.weight);

  // BMI is calculated from the existing profile.
  const heightM = Number(profile.height) / 100;
  const weightKg = Number(profile.weight);

  if (heightM > 0 && weightKg > 0) {
    payload.bmi = Number((weightKg / (heightM * heightM)).toFixed(2));
  }

  // Never send UI-only values to the ML model.
  delete payload.sex;
  delete payload.unusual_tiredness;
  delete payload.unusual_thirst;
  delete payload.frequent_urination;
  delete payload.dizziness;
  delete payload.shortness_of_breath;
  delete payload.chest_discomfort;
  delete payload.sleep_quality;
  delete payload.physical_activity;
  delete payload.diabetes_family_history;

  return payload;
}
function FeatureInput({ feature, value, onChange }: { feature: string; value: string; onChange: (v: string) => void }) {
  const key = feature.toLowerCase();
  const label = labelFor(feature);
  const options = selectOptions[key];
  const displayOptions = optionLabels[key] || {};

  const help: Record<string, string> = {
    pregnancies: "If this does not apply to you, enter 0.",
    glucose: "Use a recent blood-sugar reading if you have one.",
    blood_pressure: "Use a recent reading from a blood-pressure monitor.",
    skin_thickness: "Only enter this if it was measured during a health check.",
    insulin: "Only enter this if you have an insulin test result.",
    bmi: "Calculated automatically when height and weight are available.",
    diabetes_pedigree: "This model feature is based on family history. It is not a value you normally need to calculate yourself.",
    chol: "Use the total cholesterol value from a blood test.",
    trestbps: "Use your resting blood-pressure reading.",
    fbs: "Use your fasting blood-sugar test result.",
    restecg: "Use the result shown on your ECG report.",
    thalach: "Use the maximum heart rate recorded during an exercise test.",
    exang: "Whether chest discomfort occurred during exercise.",
    oldpeak: "Use the value from an exercise ECG report.",
    slope: "Use the pattern reported by an exercise ECG.",
    ca: "Use the number reported by a heart imaging/test report.",
    thal: "Use the result from the relevant clinical test.",
    age: "Your age in years.",
    height: "Your height in centimetres.",
    weight: "Your weight in kilograms.",
  };

  const isBinary = Boolean(options);

  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-bold text-slate-700">
        {label}
      </span>

      {help[key] && (
        <span className="mb-2 block text-xs leading-5 text-slate-400">
          {help[key]}
        </span>
      )}

      {options ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="focus-ring w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-sm outline-none focus:border-cyan-400"
        >
          <option value="">Select an option</option>
          {options.map((o) => (
            <option key={o} value={o}>
              {displayOptions[o] || o}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={isBinary ? "text" : "number"}
          step="any"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={
            key === "pregnancies"
              ? "0 if not applicable"
              : key === "bmi"
                ? "Calculated automatically"
                : `Enter ${label.toLowerCase()}`
          }
          className="focus-ring w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-sm outline-none focus:border-cyan-400"
        />
      )}
    </label>
  );
}

function ResultPage({ result, onNavigate }: { result: PredictionResult | null; onNavigate: (p: Page) => void }) {
  if (!result) return <Shell title="Screening Result" subtitle="No screening result is available yet."><div className="rounded-3xl border border-slate-200 bg-white p-10 text-center"><FileHeart className="mx-auto text-cyan-600" /><h3 className="mt-4 text-xl font-black">Run a screening first</h3><button onClick={() => onNavigate("screening")} className="mt-5 rounded-xl bg-[#0b203b] px-4 py-2.5 text-sm font-bold text-white">Start assessment</button></div></Shell>;
  return <Shell title="Your Screening Result" subtitle="A transparent view of the actual response returned by the MedPulse ML backend.">
    <div className="grid gap-5 lg:grid-cols-[.72fr_1.28fr]">
      <div className="rounded-[2rem] bg-[#0b203b] p-7 text-white"><p className="text-xs font-bold text-cyan-300">{result.disease}</p><div className="mt-8 flex justify-center"><RiskGauge score={result.risk_score} level={result.risk_level} /></div><div className="mt-8 grid grid-cols-2 gap-3"><div className="rounded-2xl bg-white/[.06] p-4"><div className="text-xs text-slate-400">Probability</div><div className="mt-1 text-xl font-black">{formatPercent(result.probability)}</div></div><div className="rounded-2xl bg-white/[.06] p-4"><div className="text-xs text-slate-400">Risk level</div><div className="mt-1 text-xl font-black">{capitalize(result.risk_level)}</div></div></div></div>
      <div className="space-y-5">
        <div className="glass rounded-3xl p-6"><div className="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-cyan-600"><CheckCircle2 size={15} /> Backend response</div><h3 className="mt-2 text-2xl font-black">Potential health risk estimate</h3><p className="mt-3 text-sm leading-6 text-slate-500">This result is an ML-based screening estimate. It is not a confirmed diagnosis.</p>{result.predicted_class && <div className="mt-5 grid gap-3 sm:grid-cols-2"><MetricCard title="Predicted class" value={result.predicted_class} note={result.predicted_class_probability != null ? `${formatPercent(result.predicted_class_probability)} class probability` : "Returned by backend"} icon={BrainCircuit} /><MetricCard title="Model" value={result.model} note={`${result.model_features} model features`} icon={Activity} /></div>}</div>
        <div className="rounded-3xl border border-amber-200 bg-amber-50 p-5"><div className="flex items-center gap-2 text-sm font-bold text-amber-900"><CircleHelp size={17} /> Medical disclaimer</div><p className="mt-2 text-sm leading-6 text-amber-800">{result.disclaimer || "This screening estimate is generated using machine-learning models and is not a medical diagnosis. Consult a qualified healthcare professional for medical advice."}</p></div>
        <div className="flex flex-wrap gap-3"><button onClick={() => onNavigate("screening")} className="rounded-xl bg-[#0b203b] px-4 py-3 text-sm font-bold text-white">New Assessment</button><button onClick={() => onNavigate("trends")} className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold">Track This Result</button><button onClick={() => onNavigate("dashboard")} className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold">Back to Dashboard</button></div>
      </div>
    </div>
    <div className="mt-5 rounded-3xl border border-slate-200 bg-white p-5"><details><summary className="cursor-pointer text-sm font-bold">Technical Details</summary><pre className="mt-4 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-5 text-slate-200">{JSON.stringify(result, null, 2)}</pre></details></div>
  </Shell>;
}

function Trends({ profile, setProfile }: { profile: UserProfile; setProfile: React.Dispatch<React.SetStateAction<UserProfile>> }) {
  type TrendPoint = { month: string; weight?: number; bmi?: number; systolic?: number; heartRate?: number };
  const [points, setPoints] = useState<TrendPoint[]>(() => { try { return JSON.parse(localStorage.getItem("medpulse-trends") || "[]"); } catch { return []; } });
  const [form, setForm] = useState({ month: "", weight: "", systolic: "", heartRate: "" });

  const add = (e: React.FormEvent) => {
    e.preventDefault();
    const weight = Number(form.weight);
    const systolic = Number(form.systolic);
    const heartRate = Number(form.heartRate);
    const bmi = profile.height && weight ? weight / Math.pow(Number(profile.height) / 100, 2) : undefined;
    const point: TrendPoint = { month: form.month || `M${points.length + 1}`, ...(Number.isFinite(weight) && weight ? { weight, bmi } : {}), ...(Number.isFinite(systolic) && systolic ? { systolic } : {}), ...(Number.isFinite(heartRate) && heartRate ? { heartRate } : {}) };
    const next = [...points, point].slice(-12);
    setPoints(next); localStorage.setItem("medpulse-trends", JSON.stringify(next)); setForm({ month: "", weight: "", systolic: "", heartRate: "" });
  };

  return <Shell title="Health Trends" subtitle="Track measurements over time. Prototype trend data is stored in browser local storage until a real health-data endpoint is connected.">
    <div className="grid gap-5 lg:grid-cols-[.7fr_1.3fr]">
      <div className="glass rounded-3xl p-5"><p className="text-xs font-black uppercase tracking-wider text-cyan-600">ADD MONTHLY MEASUREMENT</p><h3 className="mt-1 text-xl font-black">Keep the timeline honest.</h3><form onSubmit={add} className="mt-5 space-y-4"><Field label="Month label" value={form.month} onChange={(v) => setForm({ ...form, month: v })} placeholder={`M${points.length + 1}`} /><Field label="Weight (kg)" value={form.weight} onChange={(v) => setForm({ ...form, weight: v })} placeholder="82" /><Field label="Systolic blood pressure" value={form.systolic} onChange={(v) => setForm({ ...form, systolic: v })} placeholder="Optional" /><Field label="Heart rate (bpm)" value={form.heartRate} onChange={(v) => setForm({ ...form, heartRate: v })} placeholder="Optional" /><button className="w-full rounded-xl bg-[#0b203b] px-4 py-3 text-sm font-bold text-white">Save measurement</button></form><p className="mt-4 text-[11px] leading-5 text-slate-400">BMI is calculated from your saved height and the entered weight. No values are generated by MedPulse.</p></div>
      <div className="space-y-5"><TrendChart title="Weight & BMI" data={points} keys={["weight", "bmi"]} /><TrendChart title="Blood pressure & heart rate" data={points} keys={["systolic", "heartRate"]} /></div>
    </div>
  </Shell>;
}

function TrendChart({ title, data, keys }: { title: string; data: Array<Record<string, unknown>>; keys: string[] }) {
  return <div className="rounded-3xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between"><h3 className="font-bold">{title}</h3><BarChart3 size={17} className="text-cyan-600" /></div>{data.length ? <div className="mt-5 h-56"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data}><defs><linearGradient id={`g-${title}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0ea5e9" stopOpacity={.22} /><stop offset="100%" stopColor="#0ea5e9" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#e8eef4" strokeDasharray="3 3" /><XAxis dataKey="month" tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} /><Tooltip /><Area type="monotone" dataKey={keys[0]} stroke="#0ea5e9" fill={`url(#g-${title})`} connectNulls={false} /><Line type="monotone" dataKey={keys[1]} stroke="#0f766e" strokeWidth={2} dot={false} connectNulls={false} /></AreaChart></ResponsiveContainer></div> : <div className="grid h-56 place-items-center text-center text-sm text-slate-400"><div><BarChart3 className="mx-auto mb-2 text-slate-300" /><p>Add measurements to see your real trend.</p></div></div>}</div>;
}

function Assistant() {
  return <Shell title="AI Health Assistant" subtitle="ML performs the screening. A future AI layer can explain results and trends in simple language.">
    <div className="grid gap-5 lg:grid-cols-[1fr_.75fr]">
      <div className="rounded-[2rem] bg-[#0b203b] p-7 text-white"><div className="flex items-center gap-2 text-cyan-300"><Sparkles size={18} /><span className="text-xs font-black uppercase tracking-wider">Integration Ready</span></div><h3 className="mt-5 text-3xl font-black">Explain my health data without pretending to diagnose.</h3><p className="mt-4 max-w-xl text-sm leading-7 text-slate-300">This UI is intentionally not fabricating AI answers. Connect a future assistant endpoint to explain actual ML results, health trends and general wellness guidance.</p><div className="mt-8 flex items-center gap-2 text-xs font-semibold text-slate-400"><span className="rounded-full bg-white/10 px-3 py-1.5">HEALTH DATA</span><ArrowRight size={13} /><span className="rounded-full bg-white/10 px-3 py-1.5">ML RESULT</span><ArrowRight size={13} /><span className="rounded-full bg-cyan-400/15 px-3 py-1.5 text-cyan-200">AI EXPLANATION</span></div></div>
      <div className="glass rounded-[2rem] p-6"><div className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-2xl bg-cyan-50 text-cyan-600"><MessageCircle size={19} /></div><div><h3 className="font-bold">Assistant unavailable</h3><p className="text-xs text-slate-400">No AI endpoint is connected yet.</p></div></div><div className="mt-6 space-y-2">{["Explain my screening result", "Explain my health trend", "General diet guidance", "General healthy habits"].map((q) => <button disabled key={q} className="flex w-full items-center justify-between rounded-xl border border-slate-200 px-3.5 py-3 text-left text-xs font-semibold text-slate-400"><span>{q}</span><ArrowRight size={14} /></button>)}</div><div className="mt-6 rounded-2xl bg-slate-50 p-4 text-[11px] leading-5 text-slate-500">General wellness guidance will always be presented as general information, not individualized medical or nutritional advice.</div></div>
    </div>
  </Shell>;
}

function Band() {
  return <Shell title="MedPulse Band" subtitle="Your health, continuously connected — a long-term hardware vision, not a live device connection today.">
    <div className="grid gap-5 lg:grid-cols-[.85fr_1.15fr]"><div className="mesh relative min-h-[470px] overflow-hidden rounded-[2rem] p-7 text-white"><div className="absolute right-0 top-0 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" /><div className="relative"><span className="rounded-full bg-white/10 px-3 py-1.5 text-[10px] font-black text-cyan-200">COMING SOON</span><h3 className="mt-8 text-4xl font-black">MedPulse Band</h3><p className="mt-4 max-w-md text-sm leading-7 text-slate-300">A future wearable concept for continuous physiological signals that can enrich the longitudinal MedPulse health profile.</p><div className="mt-12 flex justify-center"><div className="relative h-48 w-32 rotate-[-8deg] rounded-[2.4rem] border-8 border-slate-500/40 bg-slate-900 shadow-2xl"><div className="absolute inset-5 rounded-[1.6rem] border border-cyan-300/20 bg-[#071426] p-3"><HeartPulse className="mt-8 text-cyan-300" /><div className="mt-3 text-[8px] text-slate-500">NO LIVE DATA</div></div></div></div></div></div><div className="space-y-5"><div className="grid gap-3 sm:grid-cols-2">{([["Heart Rate", HeartPulse], ["Blood Pressure", Activity], ["SpOâ‚‚", Droplets], ["Steps", Activity], ["Sleep", Moon], ["Activity", Zap]] as const).map(([name, Icon]) => <div key={String(name)} className="rounded-2xl border border-slate-200 bg-white p-4"><Icon size={18} className="text-cyan-600" /><div className="mt-4 text-sm font-bold">{String(name)}</div><div className="mt-1 text-[10px] text-slate-400">Integration ready • no live reading</div></div>)}</div><div className="rounded-3xl border border-slate-200 bg-white p-5"><p className="text-xs font-black uppercase tracking-wider text-cyan-600">FUTURE ARCHITECTURE</p><div className="mt-5 grid gap-2 sm:grid-cols-3">{["Continuous physiological data", "Longitudinal health profile", "Disease-specific ML screening", "Risk trends", "AI explanation"].map((x, i) => <div key={x} className="flex items-center gap-2 rounded-xl bg-slate-50 p-3 text-xs font-semibold text-slate-600"><span className="grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-white text-[10px] font-black text-cyan-600">{i + 1}</span>{x}</div>)}</div></div></div></div>
  </Shell>;
}

function HistoryPage({ assessments, onView }: { assessments: StoredAssessment[]; onView: (result: PredictionResult) => void }) {
  const [query, setQuery] = useState("");
  const filtered = assessments.filter((x) => `${x.disease} ${x.risk_level}`.toLowerCase().includes(query.toLowerCase()));
  return <Shell title="Assessment History" subtitle="Only actual screening results created in this browser session are shown here.">
    <div className="rounded-3xl border border-slate-200 bg-white p-5"><div className="relative max-w-sm"><Search size={16} className="absolute left-3 top-3 text-slate-400" /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search disease or risk level" className="w-full rounded-xl border border-slate-200 py-2.5 pl-9 pr-3 text-sm outline-none focus:border-cyan-400" /></div><div className="mt-5 overflow-x-auto"><table className="w-full min-w-[650px] text-left text-sm"><thead><tr className="border-b border-slate-100 text-xs text-slate-400"><th className="px-3 py-3">Date</th><th className="px-3 py-3">Disease</th><th className="px-3 py-3">Risk Score</th><th className="px-3 py-3">Risk Level</th><th className="px-3 py-3">Probability</th><th /></tr></thead><tbody>{filtered.map((a, i) => <tr key={`${a.date}-${i}`} className="border-b border-slate-50"><td className="px-3 py-3">{new Date(a.date).toLocaleDateString()}</td><td className="px-3 py-3 font-bold">{a.disease}</td><td className="px-3 py-3 font-black">{a.risk_score}</td><td className="px-3 py-3"><span className={`rounded-full px-2 py-1 text-[10px] font-black uppercase ${a.risk_level === "low" ? "bg-emerald-50 text-emerald-700" : a.risk_level === "moderate" ? "bg-amber-50 text-amber-700" : "bg-red-50 text-red-700"}`}>{a.risk_level}</span></td><td className="px-3 py-3">{formatPercent(a.probability)}</td><td className="px-3 py-3 text-right"><button onClick={() => onView(a)} className="font-bold text-cyan-700">View</button></td></tr>)}</tbody></table>{!filtered.length && <div className="py-16 text-center text-sm text-slate-400"><History className="mx-auto mb-2 text-slate-300" />No stored assessments yet.</div>}</div></div>
  </Shell>;
}

function Profile({ profile, setProfile }: { profile: UserProfile; setProfile: React.Dispatch<React.SetStateAction<UserProfile>> }) {
  const bmi = profile.height && profile.weight ? Number(profile.weight) / Math.pow(Number(profile.height) / 100, 2) : null;
  return <Shell title="Profile" subtitle="Keep your basic health information current.">
    <div className="grid gap-5 lg:grid-cols-[1fr_.55fr]"><div className="glass rounded-3xl p-6"><div className="grid gap-4 sm:grid-cols-2"><Field label="Name" value={profile.name} onChange={(v) => setProfile((p) => ({ ...p, name: v }))} placeholder="Your name" /><Field label="Email / username" value={profile.username} onChange={(v) => setProfile((p) => ({ ...p, username: v }))} placeholder="you@example.com" /><Field label="Age" value={profile.age} onChange={(v) => setProfile((p) => ({ ...p, age: v }))} placeholder="Age" /><Field label="Height (cm)" value={profile.height} onChange={(v) => setProfile((p) => ({ ...p, height: v }))} placeholder="175" /><Field label="Weight (kg)" value={profile.weight} onChange={(v) => setProfile((p) => ({ ...p, weight: v }))} placeholder="82" /></div><div className="mt-6 rounded-2xl bg-slate-50 p-4 text-xs text-slate-500">Profile data in this prototype is stored locally in your browser.</div></div><div className="rounded-3xl bg-[#0b203b] p-6 text-white"><Scale className="text-cyan-300" /><div className="mt-6 text-xs text-slate-400">CALCULATED BMI</div><div className="mt-1 text-5xl font-black">{bmi ? bmi.toFixed(1) : "—"}</div><p className="mt-3 text-sm leading-6 text-slate-400">BMI is calculated from height and weight. MedPulse does not ask you to guess your BMI.</p></div></div>
  </Shell>;
}

function SettingsPage({ onLogout }: { onLogout: () => void }) {
  const [dark, setDark] = useState(false);
  return <Shell title="Settings" subtitle="Prototype preferences and privacy controls.">
    <div className="max-w-2xl space-y-3">{([
      ["Notifications", "Keep future health reminders optional and user-controlled.", Bell, true],
      ["Privacy", "Health information is sensitive. Minimize collection and use secure communication in production.", LockKeyhole, true],
      ["Theme", "The current prototype is optimized for a light clinical dashboard.", dark ? Moon : Sun, dark],
    ] as const).map(([title, text, Icon, active], i) => <div key={String(title)} className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white p-5"><div className="flex items-start gap-4"><div className="grid h-10 w-10 place-items-center rounded-xl bg-slate-50 text-cyan-600"><Icon size={18} /></div><div><h3 className="font-bold">{String(title)}</h3><p className="mt-1 text-xs leading-5 text-slate-500">{String(text)}</p></div></div><button onClick={() => i === 2 && setDark(!dark)} className={`h-7 w-12 rounded-full p-1 ${active ? "bg-cyan-500" : "bg-slate-200"}`}><span className={`block h-5 w-5 rounded-full bg-white transition ${active ? "translate-x-5" : ""}`} /></button></div>)}<button onClick={onLogout} className="mt-5 flex items-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-3 text-sm font-bold text-red-600"><LogOut size={16} /> Log out</button></div>
  </Shell>;
}

function ErrorPanel({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return <div className="rounded-2xl border border-red-200 bg-red-50 p-5"><div className="flex gap-3"><AlertCircle className="shrink-0 text-red-500" size={18} /><div><h3 className="text-sm font-bold text-red-900">Something went wrong</h3><p className="mt-1 text-xs leading-5 text-red-700">{message}</p>{onRetry && <button onClick={onRetry} className="mt-3 rounded-lg bg-white px-3 py-2 text-xs font-bold text-red-700 shadow-sm">Retry</button>}</div></div></div>;
}

function labelFor(feature: string) {
  return featureLabels[feature.toLowerCase()] || feature.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
}
function capitalize(value: string) { return value ? value[0].toUpperCase() + value.slice(1) : value; }
function formatPercent(value: number) { return `${(value <= 1 ? value * 100 : value).toFixed(2)}%`; }

export default App;


























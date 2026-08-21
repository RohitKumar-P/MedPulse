import { useRef, useState } from "react";
import { FileText, Upload, CheckCircle2, X } from "lucide-react";
import { uploadMedicalReport } from "../services/medicalReportApi";

type Props = {
  title: string;
  description?: string;
  disease?: string;
  onFileSelected?: (file: File | null) => void;
};

export default function MedicalReportUpload({
  title,
  description,
  disease = "general",
  onFileSelected,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const selectFile = async (selected: File | null) => {
    setError("");
    setFile(selected);
    onFileSelected?.(selected);

    if (!selected) return;

    try {
      setUploading(true);
      await uploadMedicalReport(selected, disease);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "We could not process this report."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-start gap-4">
        <div className="rounded-xl bg-cyan-50 p-3 text-cyan-600">
          <FileText size={22} />
        </div>

        <div className="flex-1">
          <h3 className="font-bold text-slate-900">{title}</h3>

          {description && (
            <p className="mt-1 text-sm leading-5 text-slate-500">
              {description}
            </p>
          )}

          {!file ? (
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-bold text-white hover:bg-slate-800"
            >
              <Upload size={16} />
              Upload report
            </button>
          ) : (
            <div className="mt-4 rounded-xl bg-emerald-50 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
                  <CheckCircle2 size={17} />
                  {file.name}
                </div>

                <button
                  type="button"
                  onClick={() => selectFile(null)}
                  className="text-slate-400 hover:text-slate-700"
                >
                  <X size={17} />
                </button>
              </div>

              {uploading && (
                <p className="mt-2 text-xs text-slate-500">
                  Processing report...
                </p>
              )}
            </div>
          )}

          {error && (
            <p className="mt-3 text-sm text-red-600">
              {error}
            </p>
          )}

          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            className="hidden"
            onChange={(event) =>
              selectFile(event.target.files?.[0] || null)
            }
          />
        </div>
      </div>
    </div>
  );
}

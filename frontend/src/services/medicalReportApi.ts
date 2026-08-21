const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const REPORT_ENDPOINT =
  import.meta.env.VITE_MEDICAL_REPORT_ENDPOINT ||
  "/upload_and_analyze";

export type MedicalReportResponse = {
  success?: boolean;
  message?: string;
  data?: Record<string, unknown>;
  extracted?: Record<string, unknown>;
  [key: string]: unknown;
};

export async function uploadMedicalReport(
  file: File,
  disease: string
): Promise<MedicalReportResponse> {
  const form = new FormData();

  form.append("file", file);
  form.append("disease", disease);

  const response = await fetch(
    `${API_BASE}${REPORT_ENDPOINT}`,
    {
      method: "POST",
      body: form,
    }
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");

    throw new Error(
      text || `Report upload failed (${response.status})`
    );
  }

  return response.json();
}

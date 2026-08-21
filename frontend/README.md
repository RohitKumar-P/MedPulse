# MedPulse Frontend

React + TypeScript + Vite + Tailwind CSS + Framer Motion + Recharts frontend for the MedPulse hackathon project.

## Run

1. Copy `.env.example` to `.env`
2. Keep `VITE_API_URL=http://127.0.0.1:8000` for local FastAPI.
3. Install dependencies:

```bash
npm install
```

4. Start:

```bash
npm run dev
```

## Backend contract used

- `GET /health`
- `POST /auth/login`
- `POST /auth/register`
- `POST /auth/logout`
- `GET /predict/{disease}/schema`
- `POST /predict/{disease}`

Disease IDs:

`heart`, `diabetes`, `anemia`, `hypertension`, `breast-cancer`, `ckd`, `liver`, `parkinsons`, `stroke`, `thyroid`.

The disease form is schema-driven. The frontend does not contain prediction logic and does not fabricate result values.

## Notes

- Height + weight are used to calculate BMI when those fields are present.
- History and monthly trends use localStorage because no patient-facing history/trends endpoint was assumed.
- AI Assistant is explicitly integration-ready and does not fabricate AI answers.
- MedPulse Band is explicitly a future hardware concept and shows no live readings.
- Authentication uses the existing FastAPI auth routes.

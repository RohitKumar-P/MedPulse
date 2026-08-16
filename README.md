# MedPulse

AI-assisted health assessment and emergency assistance platform.

## Project Structure

- `backend/` — FastAPI backend, authentication, medical records, AI assessment, GPS/hospital services and emergency services.
- `frontend/` — Web frontend maintained by the frontend team.

## Backend

### Core systems

- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT authentication
- Refresh-session rotation
- AES-256-GCM patient-data encryption
- AI symptom analysis
- Critical symptom detection
- Device GPS validation
- OpenStreetMap hospital discovery
- Emergency hospital suitability ranking
- OSRM road-distance routing
- Emergency contacts

## Security

Never commit:

- `.env`
- encryption keys
- JWT secrets
- database passwords
- API keys
- patient data
- local databases

Use `.env.example` for required configuration.

## Development

Backend runs locally on:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

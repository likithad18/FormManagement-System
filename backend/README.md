# Backend (FastAPI)

This directory contains the FastAPI backend for the form management system.

## Development

- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Run the app (for local dev):
  ```bash
  uvicorn src.main:app --reload
  ```

## Database Migrations

- Initialize Alembic (if not already):
  ```bash
  alembic init alembic
  ```
- Run migrations:
  ```bash
  alembic upgrade head
  ```

## Testing

- Run all tests:
  ```bash
  pytest
  ```

## Authentication (JWT)

- Obtain a token:
  ```bash
  curl -X POST http://localhost:8000/api/auth/token -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpass"}'
  ```
- Use the access token as a Bearer token for protected endpoints.

- Refresh token:
  ```bash
  curl -X POST http://localhost:8000/api/auth/refresh -H "Content-Type: application/json" -d '{"refresh_token": "<refresh_token>"}'
  ```

## Rate Limiting

- Example rate-limited endpoint:
  ```bash
  curl http://localhost:8000/api/limited
  ```
  (Limited to 5 requests per minute per IP)

## File Upload with S3

- Upload a file:
  ```bash
  curl -F "file=@yourfile.txt" http://localhost:8000/api/upload
  ```
  Requires AWS credentials and S3 bucket configured in environment variables.

## SES Email Notification

- On file upload, an email is sent via SES if SES_EMAIL_FROM and SES_EMAIL_TO are set in the environment.

## Security Headers & HTTPS

- Security headers are set on all responses.
- To enforce HTTPS, uncomment the HTTPSRedirectMiddleware in `src/main.py`. 
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
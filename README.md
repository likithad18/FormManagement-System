# Form Management System

A full-stack AWS-powered form management system built with React, FastAPI, PostgreSQL, and Terraform.

## Project Structure

- `frontend/` - React frontend
- `backend/` - FastAPI backend
- `infrastructure/terraform/` - Terraform IaC
- `.github/workflows/` - CI/CD pipelines

---

## Running the Project

### 1. With Docker Compose (Recommended for Local Dev)

This will start the database, backend, and frontend together.

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Database: localhost:5432 (user: `formuser`, password: `formpass`, db: `formdb`)

To stop and remove containers:
```bash
docker-compose down
```

---

### 2. Running Each Service Manually

#### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

- By default, connects to PostgreSQL at `postgresql://formuser:formpass@localhost:5432/formdb`
- Configure `DATABASE_URL` env variable as needed.

##### Database Migrations

```bash
alembic upgrade head
```

##### Run Tests

```bash
pytest
```

---

#### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

- Runs at http://localhost:3000
- Expects backend at `http://localhost:8000/api` (set `VITE_API_BASE` in `.env` to override)

---

#### Database (PostgreSQL)

If not using Docker, you can run PostgreSQL locally and create the database/user:

```bash
# Example using psql
psql -U postgres
CREATE DATABASE formdb;
CREATE USER formuser WITH PASSWORD 'formpass';
GRANT ALL PRIVILEGES ON DATABASE formdb TO formuser;
```

---

## Infrastructure as Code (AWS Deployment)

See `infrastructure/terraform/README.md` for AWS deployment instructions. Example:

1. Install [Terraform](https://www.terraform.io/downloads.html)
2. Configure your AWS credentials (e.g., with `aws configure`)
3. Set required variables (see `variables.tf`). You can use a `terraform.tfvars` file:
   ```hcl
   s3_bucket_name = "your-unique-bucket-name"
   db_password    = "your-secure-password"
   ```
4. Initialize and apply:
   ```bash
   terraform init
   terraform apply
   ```

Outputs include S3 bucket name, RDS endpoint, DB name, and user.

---

## Environment Variables

- **Backend:**
  - `DATABASE_URL` (e.g., `postgresql://formuser:formpass@db:5432/formdb`)
- **Frontend:**
  - `VITE_API_BASE` (e.g., `http://localhost:8000/api`)

---

## Testing

- **Backend:**
  - Run all tests: `pytest`
- **Frontend:**
  - (Add frontend test instructions if available)

---

## CI/CD

- Automated tests and deployment via GitHub Actions in `.github/workflows/`.

---

## More

- Setup instructions, architecture diagrams, and cost optimization details coming soon. 
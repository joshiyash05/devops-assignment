# ACEest Fitness & Gym DevOps Assignment

ACEest Fitness & Gym is a no-UI Flask API created for a DevOps assignment covering application modularization, testing, Docker containerization, Jenkins builds, and GitHub Actions CI.

## Project Structure

```text
.
+-- aceest/
|   +-- __init__.py
|   +-- routes.py
|   +-- services.py
|   +-- storage.py
+-- tests/
|   +-- test_routes.py
|   +-- test_services.py
+-- .github/workflows/main.yml
+-- app.py
+-- Dockerfile
+-- Jenkinsfile
+-- requirements.txt
+-- README.md
```

The old Tkinter scripts are kept outside the production Flask app as reference material only. The Flask service is intentionally API-only.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask API:

```bash
python app.py
```

The app runs on:

```text
http://127.0.0.1:5000
```

Swagger API documentation is available at:

```text
http://127.0.0.1:5000/docs
```

The raw OpenAPI specification is available at:

```text
http://127.0.0.1:5000/openapi.json
```

## API Endpoints

```text
GET  /health
GET  /docs
GET  /openapi.json
GET  /programs
GET  /clients
POST /clients
GET  /clients/<id>
GET  /clients/<id>/summary
GET  /clients/<id>/workouts
POST /clients/<id>/workouts
```

Example client payload:

```json
{
  "name": "Asha Kumar",
  "age": 29,
  "height_cm": 168,
  "weight_kg": 66,
  "program": "Fat Loss",
  "membership_end": "2999-12-31"
}
```

## Swagger Documentation

The project includes a Swagger UI page for exploring and testing the API from a browser.

Start the Flask server first:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/docs
```

The Swagger page loads its OpenAPI schema from:

```text
http://127.0.0.1:5000/openapi.json
```

The OpenAPI server URL is configured as a relative path (`/`) so the docs work whether the app is opened through `127.0.0.1`, `localhost`, Docker port mapping, or a CI-hosted environment. The Flask app also adds CORS headers to API responses to avoid local Swagger fetch errors.

Do not open the Swagger HTML as a local file. Always access it through the Flask route:

```text
http://127.0.0.1:5000/docs
```

## Manual Testing

Run all tests:

```bash
python -m pytest
```

Run a syntax/build check:

```bash
python -m compileall app.py aceest tests
```

## Docker

Build the Docker image:

```bash
docker build -t aceest-fitness-api .
```

Run the container:

```bash
docker run --rm -p 5000:5000 aceest-fitness-api
```

Run tests inside the image:

```bash
docker run --rm aceest-fitness-api python -m pytest
```

## Jenkins Integration

The `Jenkinsfile` defines the BUILD quality gate:

```text
Checkout -> Install Dependencies -> Build and Lint -> Automated Tests -> Docker Image Assembly -> Containerized Tests
```

In Jenkins, create a Pipeline job that points to the public GitHub repository. Jenkins will pull the latest code, install dependencies in a clean environment, run validation checks, build the Docker image, and execute the pytest suite inside the container.

The Jenkins pipeline checks Docker access before running Docker stages. If the Jenkins user cannot access the Docker daemon, the pipeline still completes the Python build and pytest validation, then skips Docker image assembly and containerized tests. To run Docker stages in Jenkins, make sure Docker is installed and the Jenkins user has permission to access the Docker socket.

## GitHub Actions Integration

The workflow in `.github/workflows/main.yml` runs on every push and pull request to `main` or `master`.

Pipeline stages:

```text
Checkout repository
Set up Python
Install dependencies
Build and lint Python files
Run pytest suite
Build Docker image
Run tests inside Docker image
```

## Commit Strategy

The repository was built in focused commits:

```text
feat: add initial Flask API script
refactor: modularize Flask API structure
test: add pytest coverage for API behavior
build: add Docker image configuration
ci: automate tests and Docker build with GitHub Actions
ci: add Jenkins build pipeline
docs: add project setup and pipeline documentation
docs: add Swagger API documentation page
fix: allow Swagger requests across local origins
```

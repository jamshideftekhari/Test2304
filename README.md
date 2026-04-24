
# Flask Hello World — CI/CD Demo

A minimal Flask application used to demonstrate Continuous Integration with GitHub Actions and containerisation with Docker.

---

## Application Architecture

```
Test2304/
├── app.py              # Flask application (two routes)
├── test_app.py         # Pytest tests for both routes
├── requirements.txt    # Python dependencies (Flask)
├── Dockerfile          # Container image definition
├── .dockerignore       # Files excluded from the image
└── .github/
    └── workflows/
        └── python-app.yml   # CI pipeline definition
```

### The Application (`app.py`)

The app is a single Python file with two HTTP routes:

| Route   | Returns                          |
|---------|----------------------------------|
| `/`     | Plain text: `Hello, World!`      |
| `/time` | Current server time as a string  |

Flask is a lightweight web framework. When you run the app, it starts an HTTP server on port `5000`. Each incoming request is matched to a route function, which returns a response.

```
Browser / Client
      │
      │  HTTP GET /
      ▼
  Flask Router
      │
      ▼
  hello_world()  ──►  "Hello, World!"
```

### The Tests (`test_app.py`)

Pytest tests use Flask's built-in **test client** — a fake browser that sends requests to the app in memory, without starting a real server. Each test checks that a route returns the correct status code and response body.

---

## Continuous Integration (CI)

### What is CI?

Continuous Integration means every change pushed to the repository is **automatically verified** by running builds and tests. The goal is to catch bugs immediately, before they reach other developers or production.

Without CI:
- A developer pushes broken code.
- Nobody finds out until someone manually runs the tests — or worse, until it breaks in production.

With CI:
- Every `git push` triggers an automated pipeline.
- If tests fail, the pipeline turns red and the team is notified instantly.
- The `main` branch is always in a known-good state.

### GitHub Actions

GitHub Actions is GitHub's built-in CI/CD platform. You define pipelines as YAML files inside `.github/workflows/`. GitHub runs them automatically on events you choose (e.g. every push to `main`).

Key concepts:

| Concept    | Meaning                                                                 |
|------------|-------------------------------------------------------------------------|
| **Workflow** | The entire pipeline, defined in one `.yml` file                       |
| **Trigger**  | The event that starts the workflow (`push`, `pull_request`, etc.)     |
| **Job**      | A group of steps that run on the same machine                         |
| **Step**     | A single action — running a shell command or a pre-built Action       |
| **Runner**   | The temporary virtual machine GitHub provides to execute the job      |

### This Project's Workflow

```
git push to main
       │
       ▼
┌──────────────────────────────────┐
│  Job: build  (ubuntu-latest)     │
│                                  │
│  1. Checkout code                │
│  2. Set up Python 3.10           │
│  3. Install dependencies         │
│     (pip install flask pytest)   │
│  4. Lint with flake8             │
│  5. Run pytest                   │
└──────────────┬───────────────────┘
               │  must pass first (needs: build)
               ▼
┌──────────────────────────────────┐
│  Job: docker  (ubuntu-latest)    │
│                                  │
│  1. Checkout code                │
│  2. docker build -t flask-app .  │
└──────────────────────────────────┘
```

The `docker` job only runs if `build` passes. This means a broken Docker image can never be built from code that also has failing tests.

---

## Docker / Containerisation

### What is a Container?

A container is a lightweight, isolated package that contains:
- Your application code
- The exact runtime (Python 3.10)
- All dependencies (Flask)
- The OS libraries needed to run them

It runs the same way on every machine — your laptop, a CI runner, or a cloud server.

### How the Dockerfile Works

```dockerfile
FROM python:3.10-slim        # 1. Start from an official Python image

WORKDIR /app                 # 2. Set the working directory inside the container

COPY requirements.txt .      # 3. Copy only the dependency list first
RUN pip install -r ...       # 4. Install dependencies (cached if unchanged)

COPY . .                     # 5. Copy the rest of the application code

EXPOSE 5000                  # 6. Document that the app listens on port 5000

CMD ["python", "app.py"]     # 7. Default command to start the app
```

Steps 3–4 are separated from step 5 deliberately. Docker caches each layer. If you only change `app.py`, Docker reuses the cached dependency layer and only re-runs from step 5 onward — making rebuilds fast.

### Running Locally with Docker

```bash
# Build the image
docker build -t flask-app .

# Run a container from the image
docker run -p 5000:5000 flask-app
```

Then open `http://localhost:5000` in your browser.

The `-p 5000:5000` flag maps port 5000 on your machine to port 5000 inside the container.

### CI vs. Local vs. Production

| Environment | How the app runs          | Who manages dependencies |
|-------------|---------------------------|--------------------------|
| Local (bare)| `python app.py`           | You, via `pip install`   |
| Local (Docker) | `docker run ...`       | Docker, from the image   |
| CI (tests)  | `pytest` on a runner VM   | GitHub Actions runner    |
| CI (docker) | `docker build`            | Docker daemon on runner  |
| Production  | `docker run ...` on server| Docker, from the image   |

Docker closes the gap between these environments — the same image used in CI can be deployed directly to production.

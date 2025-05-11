# Dockerfile & Image Release Automation

This repository contains a small Python helper script, `doc-dockerfile.py`, which bootstraps a GitHub Actions workflow to:

1. Generate a basic `Dockerfile`  
2. Build a Docker image from it  
3. Save the image as a `image.tar` archive  
4. Create and push a timestamped Git tag  
5. Create a GitHub Release for that tag

---

## Prerequisites

- **Python 3**  
  - Tested on Python 3.6+.  
---

## Files

- **`doc-dockerfile.py`**  
  A Python script that creates `/\.github/workflows/gen-dockerfile.yml` containing the full CI/CD pipeline.

- **`.github/workflows/gen-dockerfile.yml`** (generated)  
  Defines a single workflow, `build-and-release`, that runs on pushes to `main`.

---

## Getting Started

1. **Clone your repo** (if you haven’t already):

   ```bash
   git clone git@github.com:ImNotVarun/Automated-Build-Deployment-Workflow.git
   cd Automated-Build-Deployment-Workflow
   ```

2. **Run the generator script**:

   ```bash
   python3 doc-dockerfile.py
   ```

   - If a workflow already exists, the script will do nothing.  
   - Otherwise, it will:
     1. Create `.github/workflows/gen-dockerfile.yml`  
     2. Prompt you to commit & push.

---

## What Happens Next

- On every push to `main`:
  1. **GitHub Actions** spins up an Ubuntu VM.  
  2. It **checks out** your code.  
  3. It **echoes** a minimal `Dockerfile`.  
  4. It **builds** the Docker image (`docker build`).  
  5. It **saves** the image as `image.tar`.  
  6. It **creates & pushes** a timestamped Git tag (`vYYYYMMDDHHMMSS`).  
  7. It **creates** a GitHub Release for that tag.  
  8. It **uploads** **only** `image.tar` as the release asset.

---


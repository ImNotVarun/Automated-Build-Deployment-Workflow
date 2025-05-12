#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/containerize-static-site.yml")

WORKFLOW_CONTENT = """\
name: Containerize Static Site

on:
  push:
    paths:
      - .github/workflows/containerize-static-site.yml

permissions:
  contents: write

jobs:
  build-and-release:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v3

      - name: Build Static Site (Vite or plain)
        run: |
          if [ -f package.json ]; then
            npm install
            npm run build
          else
            mkdir -p dist
            cp -r *.html *.css *.js dist/ 2>/dev/null || true
          fi

      - name: Generate Dockerfile
        run: |
          cat << 'EOF' > Dockerfile
          FROM nginx:alpine
          COPY dist/ /usr/share/nginx/html
          EXPOSE 80
          EOF

      - name: Build Docker image
        run: |
          docker build -t static-site:${{ github.sha }} .

      - name: Save image to tarball
        run: |
          docker save static-site:${{ github.sha }} -o image.tar

      - name: Create Git tag
        id: tag
        run: |
          TAG="v$(date +'%Y%m%d%H%M%S')"
          echo "tag=$TAG" >> $GITHUB_OUTPUT
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git tag $TAG
          git push origin $TAG
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Create Release & Upload Image
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ steps.tag.outputs.tag }}
          release_name: Release ${{ steps.tag.outputs.tag }}
          files: image.tar
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

def is_git_repo():
    return subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        stdout=subprocess.DEVNULL
    ).returncode == 0

def get_github_remote():
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
        return url if "github.com" in url else None
    except subprocess.CalledProcessError:
        return None

def create_workflow():
    WORKFLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKFLOW_PATH, "w") as f:
        f.write(WORKFLOW_CONTENT)
    print(f"📄 Created workflow at {WORKFLOW_PATH}")

def commit_and_push():
    subprocess.run(["git", "add", str(WORKFLOW_PATH)], check=True)
    subprocess.run(
        ["git", "commit", "-m", "ci: add static-site containerization workflow"],
        check=True
    )
    subprocess.run(["git", "push"], check=True)
    print("🚀 Workflow committed and pushed to GitHub")

def main():
    print("\n🛠️  Static Site Containerization via GitHub Actions\n")

    if not is_git_repo():
        print("❌ You must run this inside a Git repo.")
        sys.exit(1)

    remote = get_github_remote()
    if not remote:
        print("❌ No 'origin' remote pointing to GitHub found.")
        sys.exit(1)

    print(f"🔗 GitHub repo detected: {remote}")

    if WORKFLOW_PATH.exists():
        print("✅ Workflow already exists. Nothing to do.")
    else:
        print("➕ Generating workflow for static-site containerization…")
        create_workflow()
        answer = input("Commit & push this workflow now? (y/n): ").strip().lower()
        if answer == "y":
            commit_and_push()
        else:
            print("⚠️  Skipped commit. Push it manually when ready.")

if __name__ == "__main__":
    main()

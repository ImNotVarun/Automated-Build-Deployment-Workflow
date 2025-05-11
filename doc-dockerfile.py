#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/gen-dockerfile.yml")

WORKFLOW_CONTENT = """name: Build & Release Docker Image

on:
  push:
    branches:
      - main            # or your default branch

permissions:
  contents: write     # allow tagging & release uploads

jobs:
  build-and-release:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v3

      - name: Generate Dockerfile
        run: |
          echo "FROM alpine" > Dockerfile
          echo 'CMD ["echo","Hello from Docker"]' >> Dockerfile

      - name: Build Docker image
        run: |
          docker build -t app:${{ github.sha }} .

      - name: Save image to tarball
        run: |
          IMAGE_TAG="app-${{ github.sha }}"
          docker tag app:${{ github.sha }} $IMAGE_TAG
          docker save $IMAGE_TAG -o image.tar

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
    return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                          stdout=subprocess.DEVNULL).returncode == 0

def get_github_remote():
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
        if "github.com" in url:
            return url
        return None
    except subprocess.CalledProcessError:
        return None

def create_workflow():
    WORKFLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKFLOW_PATH, "w") as f:
        f.write(WORKFLOW_CONTENT)
    print("📄  Created workflow at: \033[1m.github/workflows/gen-dockerfile.yml\033[0m")

def commit_and_push():
    subprocess.run(["git", "add", str(WORKFLOW_PATH)])
    subprocess.run(["git", "commit", "-m", "Add Docker image build & release workflow"])
    subprocess.run(["git", "push"])
    print("🚀  Workflow committed and pushed to GitHub.")

def main():
    print("\n🛠️  \033[1mDockerfile & Docker Image Generator via GitHub Actions\033[0m\n")

    if not is_git_repo():
        print("❌  \033[91mYou are not inside a Git repository or it is not initialized.\033[0m")
        print("💡  Navigate to your GitHub project folder or initialize the repo and try again.\n")
        sys.exit(1)

    github_url = get_github_remote()
    if not github_url:
        print("❌  \033[91mNo GitHub remote named 'origin' found.\033[0m")
        print("🔗  Make sure your repo is connected to GitHub.\n")
        sys.exit(1)

    print(f"🔗  GitHub repository detected: \033[1m{github_url}\033[0m")

    if WORKFLOW_PATH.exists():
        print("✅  Workflow already exists — nothing to do!\n")
    else:
        print("📂  No workflow found to generate Dockerfile & image.")
        print("➕  Creating one for you now...\n")
        create_workflow()

        answer = input("🤖  Do you want to commit and push this workflow now? (y/n): ").strip().lower()
        if answer == "y":
            commit_and_push()
            print("\n⏳  GitHub Actions will now handle the Dockerfile generation, image build, tagging, and release.")
            print("📦  Once done, check the \033[1mReleases\033[0m tab on GitHub.\n")
        else:
            print("🚫  Skipped commit. You can manually push it later if you want.\n")

if __name__ == "__main__":
    main()

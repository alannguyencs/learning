#!/usr/bin/env python3
"""Upload lesson and quiz questions to the webapp API.

Usage:
    python upload.py <base_filename> [--project-root <path>]

Example:
    python upload.py 251215_stop_trusting_cloud_cameras_heres_what_i_use_inste
"""

import argparse
import json
import os
import re
import subprocess
import sys


def load_env(project_root):
    """Load token and API URL from .env file."""
    env_path = os.path.join(project_root, ".env")
    if not os.path.exists(env_path):
        print("ERROR: .env file not found at", env_path)
        sys.exit(1)

    token = None
    api_url = "http://localhost:8999"

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("WEBAPP_ACCESS_TOKEN="):
                token = line.split("=", 1)[1].strip()
            elif line.startswith("WEBAPP_API_URL="):
                api_url = line.split("=", 1)[1].strip()

    if not token:
        print("ERROR: Set WEBAPP_ACCESS_TOKEN in .env first. Generate one via POST /auth/token.")
        sys.exit(1)

    return token, api_url


def read_files(project_root, base_filename):
    """Read lesson, metadata, and quiz files."""
    lesson_path = os.path.join(project_root, "data/lesson", f"{base_filename}.md")
    metadata_path = os.path.join(project_root, "data/metadata", f"{base_filename}.json")
    quiz_path = os.path.join(project_root, "data/quiz", f"{base_filename}.json")

    missing = []
    if not os.path.exists(lesson_path):
        missing.append(f"data/lesson/{base_filename}.md")
    if not os.path.exists(metadata_path):
        missing.append(f"data/metadata/{base_filename}.json")
    if not os.path.exists(quiz_path):
        missing.append(f"data/quiz/{base_filename}.json")

    if missing:
        print("ERROR: Missing files:", ", ".join(missing))
        print("Run lesson-youtube or lesson-quiz-generate first.")
        sys.exit(1)

    with open(lesson_path) as f:
        lesson_content = f.read()
    with open(metadata_path) as f:
        metadata = json.load(f)
    with open(quiz_path) as f:
        questions = json.load(f)

    return lesson_content, metadata, questions


def resolve_topic(metadata):
    """Extract topic_id and topic_name from metadata channel."""
    channel = metadata["channel"]
    topic_name = channel
    topic_id = re.sub(r"\s+", "_", channel.lower())
    return topic_id, topic_name


def upload_lesson(api_url, token, topic_id, topic_name, metadata, lesson_content):
    """Upload lesson and return lesson_id."""
    payload = {
        "topic": topic_id,
        "topic_name": topic_name,
        "title": metadata["title"],
        "published_date": metadata["published_date"],
        "content": lesson_content,
    }

    with open("/tmp/lesson_upload.json", "w") as f:
        json.dump(payload, f)

    result = subprocess.run(
        [
            "curl", "-s", "--connect-timeout", "10", "--max-time", "30",
            "-X", "POST", f"{api_url}/api/lessons",
            "-H", f"Authorization: Bearer {token}",
            "-H", "Content-Type: application/json",
            "-d", "@/tmp/lesson_upload.json",
        ],
        capture_output=True,
        text=True,
    )

    try:
        data = json.loads(result.stdout)
        if "id" in data:
            print(f"Lesson uploaded: \"{metadata['title']}\" (ID: {data['id']}, Topic: {topic_name})")
            return data["id"]
        else:
            print(f"ERROR uploading lesson: {result.stdout[:200]}")
            sys.exit(1)
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR uploading lesson: {result.stdout[:200]}")
        sys.exit(1)


def upload_questions(api_url, token, questions, base_filename, lesson_id, topic_id, topic_name, lesson_name):
    """Upload quiz questions one at a time."""
    for q in questions:
        q.pop("lesson_title", None)
        q["topic_id"] = topic_id
        q["lesson_id"] = lesson_id
        q["lesson_filename"] = f"{base_filename}.md"
        q["topic_name"] = topic_name
        q["lesson_name"] = lesson_name

    success = 0
    total = len(questions)

    for i, q in enumerate(questions):
        with open("/tmp/quiz_upload.json", "w") as f:
            json.dump([q], f)

        result = subprocess.run(
            [
                "curl", "-s", "--connect-timeout", "10", "--max-time", "30",
                "-X", "POST", f"{api_url}/api/quiz/questions",
                "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json",
                "-d", "@/tmp/quiz_upload.json",
            ],
            capture_output=True,
            text=True,
        )

        try:
            data = json.loads(result.stdout)
            if "inserted" in str(data).lower():
                success += 1
                print(f"  Q{i + 1}/{total}: OK")
            else:
                print(f"  Q{i + 1}/{total}: FAILED - {result.stdout[:120]}")
                break
        except (json.JSONDecodeError, ValueError):
            print(f"  Q{i + 1}/{total}: FAILED - {result.stdout[:120]}")
            break

    return success, total


def tick_to_learn(project_root, base_filename):
    """Mark lesson as done in to_learn.md."""
    to_learn_path = os.path.join(project_root, "data/to_learn.md")
    if not os.path.exists(to_learn_path):
        return

    search = f"data/lesson/{base_filename}.md"

    with open(to_learn_path) as f:
        content = f.read()

    if search in content:
        updated = content.replace(f"- [ ] ", "- [x] ", 0)  # naive, do line-level
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if search in line and line.strip().startswith("- [ ]"):
                line = line.replace("- [ ]", "- [x]", 1)
            new_lines.append(line)

        with open(to_learn_path, "w") as f:
            f.write("\n".join(new_lines))
        print(f"Checked off in data/to_learn.md")


def cleanup():
    """Remove temp files."""
    for path in ["/tmp/lesson_upload.json", "/tmp/quiz_upload.json"]:
        if os.path.exists(path):
            os.remove(path)


def main():
    parser = argparse.ArgumentParser(description="Upload lesson and quiz questions to API")
    parser.add_argument("base_filename", help="Base filename without extension")
    parser.add_argument("--project-root", default=os.getcwd(), help="Project root directory")
    args = parser.parse_args()

    project_root = args.project_root
    base_filename = args.base_filename

    # Step 0: Load token
    token, api_url = load_env(project_root)

    # Step 1: Read files
    lesson_content, metadata, questions = read_files(project_root, base_filename)

    # Step 2: Resolve topic
    topic_id, topic_name = resolve_topic(metadata)

    # Step 3: Upload lesson
    lesson_id = upload_lesson(api_url, token, topic_id, topic_name, metadata, lesson_content)

    # Step 4 & 5: Prepare and upload quiz questions
    lesson_name = metadata["title"]
    print(f"Uploading {len(questions)} quiz questions...")
    success, total = upload_questions(
        api_url, token, questions, base_filename, lesson_id, topic_id, topic_name, lesson_name
    )

    # Step 6: Tick to-learn
    tick_to_learn(project_root, base_filename)

    # Cleanup
    cleanup()

    # Step 7: Display result
    print(f"\nResult: Lesson ID {lesson_id} ({topic_name}), {success}/{total} questions uploaded")

    if success < total:
        sys.exit(1)


if __name__ == "__main__":
    main()

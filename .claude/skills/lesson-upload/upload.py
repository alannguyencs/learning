#!/usr/bin/env python3
"""Upload lesson and quiz questions to the webapp API.

Usage:
    python upload.py <base_filename> [--project-root <path>]

Accepts either:
    - bare filename:   250218_20_quantum_cheat_codes_that_i_wish_i_knew_in_my_2
    - with channel:    themitmonk/250218_20_quantum_cheat_codes_that_i_wish_i_knew_in_my_2

The script auto-discovers files across data/lesson/, data/metadata/, and data/quiz/
by searching subdirectories if the file is not found at the top level.
"""

import argparse
import glob
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


def find_file(project_root, data_dir, filename):
    """Find a file in data_dir, checking both flat and subdirectory layouts.

    Search order:
      1. data_dir/filename           (flat)
      2. data_dir/*/filename          (one subdirectory deep)
    """
    flat = os.path.join(project_root, data_dir, filename)
    if os.path.exists(flat):
        return flat

    pattern = os.path.join(project_root, data_dir, "*", filename)
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    return None


def read_files(project_root, base_filename):
    """Read lesson, metadata, and quiz files with auto-discovery."""
    # Strip any leading channel prefix for the bare name
    bare = os.path.basename(base_filename)

    lesson_path = find_file(project_root, "data/lesson", f"{bare}.md")
    metadata_path = find_file(project_root, "data/metadata", f"{bare}.json")
    quiz_path = find_file(project_root, "data/quiz", f"{bare}.json")

    # If not found with bare name, try the full base_filename (channel/name)
    if not lesson_path:
        lesson_path = find_file(project_root, "data/lesson", f"{base_filename}.md")
    if not metadata_path:
        metadata_path = find_file(project_root, "data/metadata", f"{base_filename}.json")
    if not quiz_path:
        quiz_path = find_file(project_root, "data/quiz", f"{base_filename}.json")

    missing = []
    if not lesson_path:
        missing.append(f"data/lesson/**/{bare}.md")
    if not metadata_path:
        missing.append(f"data/metadata/**/{bare}.json")
    if not quiz_path:
        missing.append(f"data/quiz/**/{bare}.json")

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

    # Store resolved paths for later reference
    metadata["_lesson_path"] = lesson_path

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


def upload_questions(api_url, token, questions, lesson_filename, lesson_id, topic_id, topic_name, lesson_name):
    """Upload quiz questions one at a time."""
    for q in questions:
        q.pop("lesson_title", None)
        q["topic_id"] = topic_id
        q["lesson_id"] = lesson_id
        q["lesson_filename"] = lesson_filename
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

    bare = os.path.basename(base_filename)

    with open(to_learn_path) as f:
        content = f.read()

    # Match the bare filename anywhere in the line
    if bare not in content:
        return

    lines = content.split("\n")
    new_lines = []
    for line in lines:
        if bare in line and line.strip().startswith("- [ ]"):
            line = line.replace("- [ ]", "- [x]", 1)
        new_lines.append(line)

    with open(to_learn_path, "w") as f:
        f.write("\n".join(new_lines))
    print("Checked off in data/to_learn.md")


def cleanup():
    """Remove temp files."""
    for path in ["/tmp/lesson_upload.json", "/tmp/quiz_upload.json"]:
        if os.path.exists(path):
            os.remove(path)


def main():
    parser = argparse.ArgumentParser(description="Upload lesson and quiz questions to API")
    parser.add_argument("base_filename", help="Base filename without extension (e.g. '250218_my_lesson' or 'themitmonk/250218_my_lesson')")
    parser.add_argument("--project-root", default=os.getcwd(), help="Project root directory")
    args = parser.parse_args()

    project_root = args.project_root
    base_filename = args.base_filename

    # Step 0: Load token
    token, api_url = load_env(project_root)

    # Step 1: Read files (auto-discovers across subdirectories)
    lesson_content, metadata, questions = read_files(project_root, base_filename)

    # Step 2: Resolve topic
    topic_id, topic_name = resolve_topic(metadata)

    # Step 3: Upload lesson
    lesson_id = upload_lesson(api_url, token, topic_id, topic_name, metadata, lesson_content)

    # Step 4 & 5: Prepare and upload quiz questions
    lesson_name = metadata["title"]
    # Use the resolved lesson path's filename for the lesson_filename field
    lesson_filename = os.path.basename(metadata.get("_lesson_path", f"{base_filename}.md"))
    print(f"Uploading {len(questions)} quiz questions...")
    success, total = upload_questions(
        api_url, token, questions, lesson_filename, lesson_id, topic_id, topic_name, lesson_name
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

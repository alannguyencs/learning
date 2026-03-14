---
name: question-to-quiz
description: Answer a user's question about a quiz question by finding the source
  lesson and transcript. Use when user says "question to quiz", "explain this quiz",
  "why is the answer", "quiz question", or asks about a specific quiz question they
  got wrong or want explained.
---

# Question to Quiz

Answer the user's question about a quiz question by tracing it back to the source lesson and transcript: $ARGUMENTS

If the request is empty or unclear, ask the user to paste or describe the quiz question they want explained.

## Step 1: Search for the Quiz Question

1. Use Grep to search across all files in `data/quiz/` for keywords from the user's question.
2. Identify which quiz file contains the matching question. Read that quiz file and locate the exact question object.
3. Extract the filename slug (e.g., `251126_you_suck_at_prompting_ai_heres_the_secret`) — this slug is shared across `data/quiz/`, `data/lesson/`, and `data/metadata/`.

If no match is found, tell the user the question could not be found in the quiz bank and ask them to provide more detail or the exact question text.

## Step 2: Load Source Material

Using the filename slug from Step 1, read both files in parallel:

1. **Lesson note**: `data/lesson/{slug}.md` — contains the structured lesson with Summary, Connect to Known, Create Chunk, and Story sections.
2. **Metadata with transcript**: `data/metadata/{slug}.json` — contains video metadata and the full transcript.

## Step 3: Understand the Quiz Question Context

From the quiz question object found in Step 1, note:

- `question` — the question text
- `quiz_type` — recall, understanding, application, or analysis
- `correct_options` — which option(s) are correct
- `response_to_user_option_*` — the explanation for each option
- `quiz_take_away` — the key learning point
- `quiz_learnt` — what the question tests

## Step 4: Answer the User's Question

Using the lesson note, transcript, and quiz question context, provide a thorough answer:

1. **Start with the direct answer** to what the user asked (e.g., why option B is correct, why their answer was wrong).
2. **Ground it in the lesson content.** Quote or reference the specific section of the lesson note (Summary, Connect to Known, Create Chunk) that covers this concept. Include the section name for reference.
3. **Ground it in the transcript.** Find the relevant passage in the transcript where this topic was discussed. Quote the key sentence(s) from the speaker so the user can hear the original explanation in context.
4. **Connect the dots.** Explain how the lesson content and transcript support the correct answer and why the other options fall short.
5. **End with the takeaway.** Restate the `quiz_take_away` from the quiz question and, if helpful, connect it to the broader lesson theme.

Keep the response conversational and concise. The goal is to help the user genuinely understand the concept, not just memorize the correct answer.

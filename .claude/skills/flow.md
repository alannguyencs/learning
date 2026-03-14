# Lesson Skills Flow

```
+------------------------------------------------------------------+
|                     LESSON PIPELINE                               |
+------------------------------------------------------------------+
|                                                                   |
|  SETUP                                                            |
|  -----                                                            |
|  Manually add YouTube channel files to data/youtube_channels/     |
|  Or use: /lesson-scan-youtube-channels                            |
|                                                                   |
|      +-------------------------------+                            |
|      | /lesson-scan-youtube-channels  |                            |
|      | Fetch latest 10 videos/channel |                            |
|      | Merge new into checklist       |                            |
|      +---------------+---------------+                            |
|                      |                                             |
|                      v                                             |
|      +-------------------------------+                            |
|      | data/youtube_channels/*.md     |                            |
|      | - [ ] unchecked = to process   |                            |
|      | - [x] checked = done           |                            |
|      +---------------+---------------+                            |
|                      |                                             |
|            +---------+---------+                                   |
|            |                   |                                   |
|            v                   v                                   |
|   (one at a time)      (batch all)                                |
|            |                   |                                   |
|            v                   v                                   |
|  +------------------+  +------------------------+                 |
|  | /lesson-youtube   |  | /lesson-batch-process  |                |
|  | Single video URL  |  | Loops all unchecked:   |                |
|  | -> metadata JSON  |  |  1. /lesson-youtube    |                |
|  | -> lesson .md     |  |  2. Mark [x] in channel|                |
|  +--------+---------+  |  3. Add to to_learn.md |                 |
|           |             +----------+-------------+                |
|           v                        |                               |
|  +------------------+              |                               |
|  | Manually review  |<-------------+                               |
|  | & edit lesson    |                                              |
|  +--------+---------+                                              |
|           |                                                        |
|           v                                                        |
|  +------------------+                                              |
|  | /lesson-quiz-    |                                              |
|  |  generate        |                                              |
|  | 10 quiz questions|                                              |
|  | -> quiz JSON     |                                              |
|  +--------+---------+                                              |
|           |                                                        |
|           v                                                        |
|  +------------------+                                              |
|  | /lesson-upload   |                                              |
|  | Upload to webapp:|                                              |
|  |  1. POST lesson  |                                              |
|  |  2. POST quiz Qs |                                              |
|  +--------+---------+                                              |
|           |                                                        |
|           v                                                        |
|      [ Lesson live in webapp ]                                     |
|                                                                    |
+------------------------------------------------------------------+
|  FILES PRODUCED AT EACH STAGE:                                    |
|                                                                   |
|  scan-channels -> data/youtube_channels/{channel}.md              |
|  lesson-youtube -> data/metadata/{yymmdd}_{slug}.json             |
|                    data/lesson/{yymmdd}_{slug}.md                  |
|  batch-process  -> data/to_learn.md (tracks new lessons)          |
|  quiz-generate  -> data/quiz/{yymmdd}_{slug}.json                 |
|  lesson-upload  -> POST /api/lessons + POST /api/quiz/questions   |
+------------------------------------------------------------------+
```

# Chrome Test Execution

After implementation is complete, execute the Chrome Claude Extension E2E tests defined in `docs/chrome_test/{feature_name}.md` (generated in Step 1.6).

Reference `docs/chrome_test/comment_thread.md` as an example of a completed test file with all reports filled in.

## Execution Steps

For each test:
- Run the database seed SQL and cleanup from the test file
- Execute each checklist step through real browser interactions
- Mark steps as `- [x]` when completed
- Update the **Report** status from `IN QUEUE` to `SUCCESS` or `FAIL`
- Add itemized findings and **Improvement Proposals** formatted as:
  `+ {priority} - {proposal name} - brief description`
  where priority is `must have` or `good to have`. Write `none` if no improvements are needed.

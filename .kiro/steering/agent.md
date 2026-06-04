# Ithaca — Agent rules (for Kiro)

- NEVER ask the user to manually check, test, or verify anything.
- Iterate autonomously until the task is complete and verified.
- There should be NO manual steps required from the user.
- The last step of every task MUST be self-verification and validation (run the app, hit endpoints, confirm output).
- Only mark a task as complete after you have personally confirmed it works.
- If something fails, fix it yourself — do not report the failure and wait.

## Examples

### ❌ WRONG — asking user to run things manually
> "The app is stopped now. To run it anytime:
> `cd ~/Projects/ithaca && source .venv/bin/activate && python -u -c "..."`
> Ready for Phase 3 whenever you want to continue."

### ✅ RIGHT — do it yourself, confirm it works
> "I've started the app, verified /health returns 200, confirmed login works with the admin credentials, and tested the chat endpoint returns a streaming response. Phase 2 complete."

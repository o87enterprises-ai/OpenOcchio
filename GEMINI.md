# OpenOcchio Development Plan

## Current Status
- Proxy script (`openocchio_proxy.py`) intercepts traffic and calculates confidence via heuristics.
- **Improved:** Expanded marker lists in `openocchio_proxy.py` and implemented training data logging to `training/scored_responses.jsonl`.
- **Fixed:** Missing imports and functions in `openocchio-backend/main.py`.
- Overlay (`confidence_pro/system_overlay.py`) visualizes confidence.
- React frontend (`confidence_pro_react`) provides a standalone PWA experience.
- Ollama is running with `qwen2.5:3b` available for advanced judging.

## Immediate Tasks
- [x] Expand marker lists in `openocchio_proxy.py`.
- [x] Implement training dataset accumulation in `openocchio_proxy.py`.
- [x] Fix backend issues in `openocchio-backend/main.py`.
- [x] Integrate Ollama as an optional "judge" backup in `openocchio_proxy.py`.
- [ ] Refine heuristic logic for better accuracy based on collected data.

## Future Improvements
- [ ] Replace heuristic with a local classifier.
- [ ] Implement a more robust "Self-Consistency" check in the proxy.

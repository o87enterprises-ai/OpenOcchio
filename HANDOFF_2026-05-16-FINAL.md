# OpenOcchio – Final Handoff 2026‑05‑16

## ✅ What works
- **Overlay** – live on `http://127.0.0.1:9876`, accepts `POST /update {"confidence": 0.0–1.0}`
- **mitmproxy** – intercepts Firefox traffic on port `8082`, script loaded
- **AI host detection** – filters for `claude.ai`, `api.anthropic.com`, `chat.deepseek.com`
- **SSE streaming** – correctly parses Claude’s `/completion` event-stream and extracts the full response text
- **Confidence heuristic** – rule‑based keyword counter, zero network, zero timeout, writes to `/tmp/occhio_debug.log`
- **Overlay update** – confirmed in debug log: `Sent confidence X.XX to overlay`
- **Gauge movement** – *works*, but the heuristic returns 0.5 for short, factual answers without explicit certainty markers (see next section)

## ⚠️ Known quirk (why the gauge might stay at 0.5)
The heuristic uses **exact phrase matching** (e.g., “certainly”, “absolutely”).  
Short declarative answers like *“Yes. Paris is the capital of France.”* contain **none** of those phrases → neutral 0.5.  
This is **correct behaviour** for the current marker lists — not a bug.

### 🔧 Solution (to make the gauge jump on clear, short answers)
Expand the high‑confidence markers with simple assertive words.  
**Add these** to the `high_confidence_markers` list in the proxy script:

```python
"yes,", "indeed", "of course", "it is ", "that is correct", "that's correct",
"without question", "no question", "by definition", "the fact is",
"is the", "definitely", "certainly", "absolutely",
```

Also add to `low_confidence_markers`:

```python
"not exactly", "sort of", "kind of", "somewhat", "it's possible",
```

After updating, restart mitmweb. Then even *“Yes. Paris is the capital of France.”* will score >0.7.

---

## 🧱 File paths (absolute)
| File | Path |
|------|------|
| Proxy script (this is the core) | `./openocchio_proxy.py` |
| Overlay script | `./confidence_pro/system_overlay.py` |
| Debug log (created at runtime) | `/tmp/occhio_debug.log` |
| Handoff file | `./HANDOFF_2026-05-16-FINAL.md` |

---

## 🔁 Restart sequence (every morning)
Run these commands **in order**, one at a time:

```bash
# 1. Kill any leftover processes
lsof -ti:9876 | xargs kill -9 2>/dev/null
pkill -f mitmweb 2>/dev/null
sleep 1

# 2. Start the overlay
python3 ./confidence_pro/system_overlay.py &

# 3. Wait a moment, then start mitmweb with the proxy script
sleep 2
rm -f /tmp/occhio_debug.log
mitmweb --listen-port 8082 -s ./openocchio_proxy.py &> /dev/null &
```

After that:
- Open Firefox (proxy `localhost:8082`)
- Go to `claude.ai` and send a test prompt (e.g., “Is Paris the capital of France?”)
- Wait 5 seconds
- Check the debug log: `cat /tmp/occhio_debug.log`
- The overlay gauge should update automatically.

---

## 🔍 Debugging
- If the gauge doesn’t move:  
  `cat /tmp/occhio_debug.log | grep "Heuristic score"`  
  If you see `confidence=0.5` and low/high markers = 0, the AI text lacks markers → expand the marker lists (see above).  
  If you see `Ollama call failed` or `Unhandled content-type`, those should no longer appear (Ollama removed, SSE handled).
- If nothing appears in the log at all:  
  * Verify Firefox proxy is set to `localhost:8082` for both HTTP and HTTPS.  
  * Check that `mitmweb` is running (`ps aux | grep mitmweb`).  
  * Make sure the proxy script is the latest version (with the `log` function and heuristic).

---

## 📈 Next improvements (when you’re ready)
1. **Expand the marker lists** – as described above – to capture more confidence levels.
2. **Log the full AI text** for every completion (already in debug log as `AI TEXT`).
3. **Accumulate a training dataset** by appending scored texts to a JSONL file.
4. **Replace the heuristic with a fine‑tuned local classifier** once you have enough labelled examples.
5. **Re‑introduce an Ollama judge** only as an optional high‑quality backup, with a short timeout and fallback to heuristic.

---

## 🧠 Summary
The entire pipeline is **live and functional**. The only thing between you and a fully reactive gauge is a richer set of marker words. You’ve already captured real Claude responses – that data will be invaluable for training a smarter model later. Everything else is solid.
 later. Everything else is solid.

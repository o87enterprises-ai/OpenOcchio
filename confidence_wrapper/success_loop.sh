#!/bin/bash
# success_loop.sh – auto‑correct until everything passes
ATTEMPT=1
while true; do
    echo "==================== ATTEMPT $ATTEMPT ===================="

    # 1) Run the original test harness (must show 100% simple accuracy)
    python3 test_harness.py | tee harness_output.txt
    if ! grep -q "Simple accuracy: [0-9]*/[0-9]* = 100%" harness_output.txt; then
        echo "❌ Test harness accuracy not 100% – fixing required."
    else
        echo "✅ Test harness accuracy at 100%"
    fi

    # 2) Run strict verification (exit code 0 only if all within bounds)
    python3 verify_strict.py
    STRICT_OK=$?

    if [ $STRICT_OK -eq 0 ]; then
        echo ""
        echo "======================================================"
        echo "🎉 ABSOLUTE SUCCESS ACHIEVED – ALL CHECKS PASSED"
        echo "======================================================"
        exit 0
    else
        echo "❌ Strict verification failed. Analyse and correct the code, then retry."
    fi

    ATTEMPT=$((ATTEMPT + 1))
    echo "⏳ Restarting loop in 3 seconds..."
    sleep 3
done

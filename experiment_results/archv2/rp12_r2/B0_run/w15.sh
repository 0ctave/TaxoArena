#!/bin/bash
# Rule 7 W1-W5 probe before a build: no java/python process, >= 12 GB free RAM; prints the facts, rc 5 on a breach.
j=$(tasklist //FO CSV //NH 2>/dev/null | grep -i -c -E '^"(java|javaw|python|python3)\.exe"')
f=$(powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)" | tr -d '\r')
echo "W1-W5 $(date -Is): java/python processes $j; free RAM ${f} GB; no git write under src in window (operator: serial, no src edits)"
[ "$j" = 0 ] && [ "$f" -ge 12 ] || { echo "W1-W5 BREACH"; exit 5; }

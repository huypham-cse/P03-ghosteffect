#!/bin/bash
# Device Farm K-9 run R1 (pre-registered in team/b-log.md, 24/11): Table 1a on a rented Galaxy A36. Five trials of the
# rig that reproduced the trap on the A36 pilot p01 (18/11) without changes: K-9 with a Sent folder, lost SMTP reply,
# force-stop, relaunch, observe 60 s, then the scripted GUI redo (recompose and Send) and 30 s more. Grading as on the
# emulator (copies on GreenMail, Message-IDs). Abort rule as the CalDAV runs: two INVALID trials in a row stop the run.
set -u
cd "$DEVICEFARM_TEST_PACKAGE_PATH"
LOG="$DEVICEFARM_LOG_DIR"
ADB="$(command -v adb)"
SERIAL="$DEVICEFARM_DEVICE_UDID"
S() { timeout 60 "$ADB" -s "$SERIAL" shell "$@" 2>&1 | tr -d '\r'; }
{
    for p in ro.product.manufacturer ro.product.model ro.build.version.release ro.build.version.sdk \
             ro.build.version.oneui ro.build.display.id; do
        echo "$p=$(S getprop $p)"
    done
} > "$LOG/device.txt"
S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard; S svc power stayon usb
S settings put global stay_on_while_plugged_in 7
streak=0
for name in k01 k02 k03 k04 k05; do
    S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard
    GX_PHYSICAL_SERIAL="$SERIAL" timeout 900 python3 testbed/k9_fault_case.py --config sent --adb "$ADB" \
        --adb-server-port 5037 --serial "$SERIAL" --java java --observe 60 --action recompose --action-window 30 \
        --output "$LOG/$name" > "$LOG/$name.log" 2>&1
    verdict=$(python3 -c "import json; print(json.load(open('$LOG/$name/RESULT.json')).get('verdict'))" 2>&1)
    echo "$(date -u +%H:%M:%S) $name $verdict" >> "$LOG/batch.log"
    case "$verdict" in INVALID*) streak=$((streak + 1));; *) streak=0;; esac
    if [ $streak -ge 2 ]; then
        echo "$(date -u +%H:%M:%S) ABORT: rig failure ($name)" >> "$LOG/batch.log"
        break
    fi
done
"$ADB" -s "$SERIAL" reverse --remove-all
echo "$(date -u +%H:%M:%S) CAMPAIGN DONE" >> "$LOG/batch.log"

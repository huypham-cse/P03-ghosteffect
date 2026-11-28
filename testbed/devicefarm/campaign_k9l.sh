#!/bin/bash
# Device Farm K9L, K-9 long observation (pre-registered in team/b-log.md, 25/11). Usage: campaign_k9l.sh 1|2
# The emulator K9L's four cases, two per phone: 1 = nosent + force-stop, sent + background; 2 = nosent + background,
# sent + force-stop. Lost SMTP reply after the commit as in R1, then 2,100 s of observation after the relaunch (more
# than two of K-9's 15-minute poll cycles); no redo. Graded from the server (copies, new SMTP DATA after the fault).
# Abort rule as R1: two INVALID trials in a row stop the run.
set -u
cd "$DEVICEFARM_TEST_PACKAGE_PATH"
LOG="$DEVICEFARM_LOG_DIR"
ADB="$(command -v adb)"
SERIAL="$DEVICEFARM_DEVICE_UDID"
S() { timeout 60 "$ADB" -s "$SERIAL" shell "$@" 2>&1 | tr -d '\r'; }
case "${1:-1}" in 1) CASES="l01:nosent:force-stop l02:sent:background";; 2) CASES="l03:nosent:background l04:sent:force-stop";;
    *) echo "unknown set $1" >> "$LOG/batch.log"; exit 0;; esac
{
    for p in ro.product.manufacturer ro.product.model ro.build.version.release ro.build.version.sdk \
             ro.build.version.oneui ro.build.display.id; do
        echo "$p=$(S getprop $p)"
    done
} > "$LOG/device.txt"
S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard; S svc power stayon usb
S settings put global stay_on_while_plugged_in 7
streak=0
for item in $CASES; do
    name=${item%%:*}; rest=${item#*:}; config=${rest%%:*}; kill=${rest#*:}
    S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard
    GX_PHYSICAL_SERIAL="$SERIAL" timeout 2700 python3 testbed/k9_fault_case.py --config "$config" --kill "$kill" \
        --adb "$ADB" --adb-server-port 5037 --serial "$SERIAL" --java java --observe 2100 \
        --output "$LOG/$name" > "$LOG/$name.log" 2>&1
    verdict=$(python3 -c "import json; print(json.load(open('$LOG/$name/RESULT.json')).get('verdict'))" 2>&1)
    echo "$(date -u +%H:%M:%S) $name $config $kill $verdict" >> "$LOG/batch.log"
    case "$verdict" in INVALID*) streak=$((streak + 1));; *) streak=0;; esac
    if [ $streak -ge 2 ]; then
        echo "$(date -u +%H:%M:%S) ABORT: rig failure ($name)" >> "$LOG/batch.log"
        break
    fi
done
"$ADB" -s "$SERIAL" reverse --remove-all
echo "$(date -u +%H:%M:%S) CAMPAIGN DONE" >> "$LOG/batch.log"

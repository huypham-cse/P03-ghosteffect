#!/bin/bash
# Device Farm polish runs TN2 and TN3 (pre-registered in team/b-log.md, 19/11). Usage: campaign_tn.sh ledger|ledger+doze
#  ledger:      TN3 only, the phone ledger benchmark (testbed/phone_ledger/harness.py, 100 kills).
#  ledger+doze: TN3, then TN2 on the same phone: dev-c00 none, e01 and e02 stop-app-doze with Doze held 600 s and
#               observation up to 1,800 s after Doze exit (stop 20 s after the retry PUT; if none, DAVx5 is opened
#               once for 90 s). Same rig, Radicale, DAVx5 setup and abort rule as campaign_caldav.sh (R1d).
set -u
MODE="${1:-ledger}"
cd "$DEVICEFARM_TEST_PACKAGE_PATH"
export GX_PHYSICAL_SERIAL="$DEVICEFARM_DEVICE_UDID" GX_RADICALE_PYTHON="$(command -v python3)" PYTHONPATH="$HOME/radlib"
LOG="$DEVICEFARM_LOG_DIR"
ADB="$(command -v adb)"
S() { timeout 60 "$ADB" -s "$GX_PHYSICAL_SERIAL" shell "$@" 2>&1 | tr -d '\r'; }
{
    for p in ro.product.manufacturer ro.product.model ro.build.version.release ro.build.version.sdk \
             ro.build.version.oneui ro.build.display.id; do
        echo "$p=$(S getprop $p)"
    done
    S dumpsys activity settings | grep -E '^ *use_freezer=' | head -1
} > "$LOG/device.txt"
S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard; S svc power stayon usb
S settings put global stay_on_while_plugged_in 7

echo "$(date -u +%H:%M:%S) TN3 ledger start" >> "$LOG/batch.log"
timeout 1200 python3 testbed/phone_ledger/harness.py --adb "$ADB" --serial "$GX_PHYSICAL_SERIAL" \
    --apk testbed/phone_ledger/ledgerbench.apk --out "$LOG/ledger" --kills 100 --seed 7 > "$LOG/ledger.log" 2>&1
echo "$(date -u +%H:%M:%S) TN3 ledger exit $?" >> "$LOG/batch.log"
if [ "$MODE" = "ledger+dump" ]; then
    # TN3b (b-log 21/11): wall time of one accessibility read as our reader takes it (adb shell uiautomator dump),
    # 20 times on the home screen; nothing is read from any app.
    S input keyevent KEYCODE_HOME > /dev/null
    echo "i,ms,exit" > "$LOG/dump_times.csv"
    for i in $(seq 1 20); do
        t0=$(date +%s%N); timeout 60 "$ADB" -s "$GX_PHYSICAL_SERIAL" shell uiautomator dump /sdcard/gx_dump.xml > /dev/null 2>&1; rc=$?
        t1=$(date +%s%N); echo "$i,$(( (t1 - t0) / 1000000 )),$rc" >> "$LOG/dump_times.csv"
    done
    S rm -f /sdcard/gx_dump.xml
    echo "$(date -u +%H:%M:%S) CAMPAIGN DONE" >> "$LOG/batch.log"
    exit 0
fi
[ "$MODE" = "ledger+doze" ] || { echo "$(date -u +%H:%M:%S) CAMPAIGN DONE" >> "$LOG/batch.log"; exit 0; }

for apk in at.bitfire.davdroid_405210002.apk ws.xsoh.etar_57.apk; do
    echo "$apk: $(timeout 180 "$ADB" -s "$GX_PHYSICAL_SERIAL" install -r -g "runtime/assets/$apk" 2>&1 | tail -1)"
done > "$LOG/install.txt"
S appops set ws.xsoh.etar SCHEDULE_EXACT_ALARM allow
echo "etar exact alarm: $(S appops get ws.xsoh.etar SCHEDULE_EXACT_ALARM)" >> "$LOG/install.txt"
python3 -c "import sys; sys.path.insert(0, 'testbed'); import caldav_fault_case as c; \
c.start_radicale(c.ROOT / 'runtime' / 'radicale.log'); print('MKCALENDAR', c.make_calendar())" > "$LOG/radicale_start.txt" 2>&1
"$ADB" -s "$GX_PHYSICAL_SERIAL" reverse tcp:5233 tcp:5232
if ! python3 testbed/devicefarm/davx5_setup.py "$ADB" "$GX_PHYSICAL_SERIAL" > "$LOG/davx5_setup.json" 2>&1; then
    S uiautomator dump /sdcard/gx_ui.xml > /dev/null; "$ADB" -s "$GX_PHYSICAL_SERIAL" pull /sdcard/gx_ui.xml "$LOG/setup_fail.xml"
    echo "DAVx5 setup failed" >> "$LOG/batch.log"
    exit 0
fi
sleep 10
"$ADB" -s "$GX_PHYSICAL_SERIAL" reverse tcp:5233 tcp:5233
S am stop-app at.bitfire.davdroid

streak=0
for item in dev-c00:none e01:stop-app-doze e02:stop-app-doze; do
    name=${item%%:*}; fault=${item#*:}
    timeout 3000 python3 testbed/caldav_fault_case.py --adb "$ADB" --adb-server-port 5037 --serial "$GX_PHYSICAL_SERIAL" \
        --fault "$fault" --doze-seconds 600 --window 1800 --until-put --nudge-open --output "$LOG/$name" > "$LOG/$name.log" 2>&1
    line=$(python3 -c "import json; r = json.load(open('$LOG/$name/RESULT.json')); \
print(r.get('verdict'), r.get('first_put_after_fault_s'), r.get('first_put_after_nudge_s'), r.get('reason', ''))" 2>&1)
    echo "$(date -u +%H:%M:%S) $name $fault $line" >> "$LOG/batch.log"
    case "$line" in INVALID*) streak=$((streak + 1));; *) streak=0;; esac
    if { [ "${name#dev}" != "$name" ] && [ $streak -ge 1 ]; } || [ $streak -ge 2 ]; then
        echo "$(date -u +%H:%M:%S) ABORT: rig failure ($name)" >> "$LOG/batch.log"
        break
    fi
done
"$ADB" -s "$GX_PHYSICAL_SERIAL" reverse --remove-all
echo "$(date -u +%H:%M:%S) CAMPAIGN DONE" >> "$LOG/batch.log"

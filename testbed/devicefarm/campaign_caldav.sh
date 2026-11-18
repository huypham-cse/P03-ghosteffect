#!/bin/bash
# Device Farm DAVx5 campaign (pre-registered in team/b-log.md, 18/11): one rented phone, trials in the frozen order
# below. Runs on the test host from the unpacked package; writes everything under $DEVICEFARM_LOG_DIR.
# The phone is wiped after the run, so the settings changed here (stay awake, forced Doze) do not outlive it.
set -u
cd "$DEVICEFARM_TEST_PACKAGE_PATH"
export GX_PHYSICAL_SERIAL="$DEVICEFARM_DEVICE_UDID" GX_RADICALE_PYTHON="$HOME/radvenv/bin/python"
LOG="$DEVICEFARM_LOG_DIR"
ADB="$(command -v adb)"
S() { timeout 60 "$ADB" -s "$GX_PHYSICAL_SERIAL" shell "$@" 2>&1 | tr -d '\r'; }
SCHEDULE="dev-c00:none c01:none c02:stop-app c03:none c04:stop-app c05:none c06:stop-app d01:stop-app-doze d02:stop-app-doze d03:stop-app-doze"

{
    for p in ro.product.manufacturer ro.product.model ro.build.version.release ro.build.version.sdk \
             ro.build.version.oneui ro.build.display.id; do
        echo "$p=$(S getprop $p)"
    done
    S dumpsys activity settings | grep -E '^ *use_freezer=' | head -1
} > "$LOG/device.txt"
S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard; S svc power stayon usb
S settings put global stay_on_while_plugged_in 7
for apk in at.bitfire.davdroid_405210002.apk ws.xsoh.etar_57.apk; do
    echo "$apk: $(timeout 180 "$ADB" -s "$GX_PHYSICAL_SERIAL" install -r -g "runtime/assets/$apk" 2>&1 | tail -1)"
done > "$LOG/install.txt"
python3 -c "import sys; sys.path.insert(0, 'testbed'); import caldav_fault_case as c; \
c.start_radicale(c.ROOT / 'runtime' / 'radicale.log'); print('MKCALENDAR', c.make_calendar())" > "$LOG/radicale_start.txt" 2>&1

# Setup reaches Radicale directly; trials reach it through the fault proxy on the same phone-side port. DAVx5 is
# then stopped once so that no pooled connection from setup is reused.
"$ADB" -s "$GX_PHYSICAL_SERIAL" reverse tcp:5233 tcp:5232
if ! python3 testbed/devicefarm/davx5_setup.py "$ADB" "$GX_PHYSICAL_SERIAL" > "$LOG/davx5_setup.json" 2>&1; then
    S uiautomator dump /sdcard/gx_ui.xml > /dev/null; "$ADB" -s "$GX_PHYSICAL_SERIAL" pull /sdcard/gx_ui.xml "$LOG/setup_fail.xml"
    echo "DAVx5 setup failed" >> "$LOG/batch.log"
    exit 0
fi
sleep 10
"$ADB" -s "$GX_PHYSICAL_SERIAL" reverse tcp:5233 tcp:5233
S am stop-app at.bitfire.davdroid

for item in $SCHEDULE; do
    name=${item%%:*}; fault=${item#*:}
    timeout 1500 python3 testbed/caldav_fault_case.py --adb "$ADB" --adb-server-port 5037 --serial "$GX_PHYSICAL_SERIAL" \
        --fault "$fault" --output "$LOG/$name" > "$LOG/$name.log" 2>&1
    echo "$(date -u +%H:%M:%S) $name $fault $(python3 -c "import json; r = json.load(open('$LOG/$name/RESULT.json')); \
print(r.get('verdict'), r.get('first_put_after_fault_s'), r.get('reason', ''))" 2>&1)" >> "$LOG/batch.log"
done
"$ADB" -s "$GX_PHYSICAL_SERIAL" reverse --remove-all
echo "$(date -u +%H:%M:%S) CAMPAIGN DONE" >> "$LOG/batch.log"

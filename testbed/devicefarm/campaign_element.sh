#!/bin/bash
# Device Farm Element runs (pre-registered in team/b-log.md, 24/11). Usage: campaign_element.sh dev|A|B
#   dev: P0, the rig check on one phone (schedule tn4x_dev.json, not counted); A, B: the two halves of the TN4 transfer
#   check (tn4x_A.json, tn4x_B.json), one phone each, in parallel.
# Same rig as the emulator runs: Synapse 1.164.2 on the host (synapse_host.py, fresh test accounts), Element 1.6.62
# (arm64 build of the same release) signed in by element_setup.py, then element_planner.py collect, unmodified, with
# the emulator calibration store testbed/tn4/tn4_store.json. The phone is wiped after the run.
set -u
MODE="${1:-dev}"
cd "$DEVICEFARM_TEST_PACKAGE_PATH"
LOG="$DEVICEFARM_LOG_DIR"
ADB="$(command -v adb)"
SERIAL="$DEVICEFARM_DEVICE_UDID"
S() { timeout 60 "$ADB" -s "$SERIAL" shell "$@" 2>&1 | tr -d '\r'; }
note() { echo "$(date -u +%H:%M:%S) $*" >> "$LOG/batch.log"; }
case "$MODE" in dev) SCHEDULE=tn4x_dev.json;; A) SCHEDULE=tn4x_A.json;; B) SCHEDULE=tn4x_B.json;;
    *) note "unknown mode $MODE"; exit 0;; esac

{
    for p in ro.product.manufacturer ro.product.model ro.build.version.release ro.build.version.sdk \
             ro.build.version.oneui ro.build.display.id; do
        echo "$p=$(S getprop $p)"
    done
    S dumpsys activity settings | grep -E '^ *use_freezer=' | head -1
} > "$LOG/device.txt"
S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard; S svc power stayon usb
S settings put global stay_on_while_plugged_in 7
note "mode $MODE schedule $SCHEDULE"

echo "$(timeout 300 "$ADB" -s "$SERIAL" install -r -g runtime/assets/im.vector.app_40106622.apk 2>&1 | tail -1)" \
    > "$LOG/install.txt"
S dumpsys package im.vector.app | grep -E 'versionCode|versionName' | head -2 >> "$LOG/install.txt"
ACCOUNTS="$HOME/element.local.json"
if ! PYTHONPATH="$HOME/synlib" python3 testbed/devicefarm/synapse_host.py --dir "$HOME/synstate" \
        --accounts "$ACCOUNTS" > "$LOG/synapse_start.json" 2> "$LOG/synapse_start.err"; then
    note "ABORT: Synapse did not start"; exit 0
fi
# Setup reaches Synapse directly; element_planner.py then points the same phone port at its fault proxy.
"$ADB" -s "$SERIAL" reverse tcp:18008 tcp:8008
if ! timeout 900 python3 testbed/devicefarm/element_setup.py "$ADB" "$SERIAL" "$ACCOUNTS" \
        > "$LOG/element_setup.json" 2> "$LOG/element_setup.err"; then
    note "ABORT: Element setup failed (no screen dump kept: it may show the test password)"; exit 0
fi
"$ADB" -s "$SERIAL" reverse --remove tcp:18008
note "setup done"
GX_ELEMENT_ACCOUNTS="$ACCOUNTS" timeout 7800 python3 testbed/element_planner.py collect \
    --schedule "testbed/devicefarm/$SCHEDULE" --store testbed/tn4/tn4_store.json --adb "$ADB" --serial "$SERIAL" \
    --out "$LOG/tn4x-$MODE" > "$LOG/collect.log" 2>&1
note "collect exit $?"
"$ADB" -s "$SERIAL" reverse --remove-all
note "CAMPAIGN DONE"

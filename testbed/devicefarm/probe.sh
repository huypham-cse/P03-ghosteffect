#!/bin/bash
# Device Farm pilot probe (b-log 18/11): what a rented, non-root phone lets the host observe and do over adb.
# Runs on the Device Farm test host from the unpacked test package. Writes text files under $DEVICEFARM_LOG_DIR/probe.
# Every device command is bounded by a timeout and never fails the run. Rented phones are wiped after the run,
# so settings changed here (stay awake, Doze, battery override) do not outlive it.
set -u
OUT="${DEVICEFARM_LOG_DIR:-/tmp}/probe"
mkdir -p "$OUT"
SERIAL="$DEVICEFARM_DEVICE_UDID"
S() { timeout 60 adb -s "$SERIAL" shell "$@" 2>&1 | tr -d '\r'; }
log() { echo "== $(date -u +%H:%M:%S) $*"; }
K9=com.fsck.k9
DAV=at.bitfire.davdroid

proc() {  # one sample of a package's process: Android's view (procstate, adj, frozen) and the kernel's view
    local pkg=$1 label=$2 pid
    pid=$(S pidof "$pkg")
    echo "-- $label $(date -u +%H:%M:%S) pid=${pid:-none} bucket=$(S am get-standby-bucket "$pkg")"
    S "dumpsys activity processes $pkg" | grep -iE 'ProcessRecord|procstate|curAdj|setAdj|frozen|freez|cached|lastPss' | head -20
    S "dumpsys activity lru" | grep -F "$pkg" | head -3
    if [ -n "$pid" ]; then
        S "cat /proc/$pid/status" | grep -E '^(State|Uid):'
        S "cat /proc/$pid/cgroup"
        S "ls -d /sys/fs/cgroup/uid_*/pid_$pid" | head -2
        S "cat /sys/fs/cgroup/uid_*/pid_$pid/cgroup.freeze /sys/fs/cgroup/uid_*/pid_$pid/cgroup.events" | head -6
        S "ps -o PID,S,NI,PCY,NAME -p $pid"
    fi
}

alive() { [ -n "$(S pidof "$1")" ] && echo alive || echo dead; }

launch() { S "monkey -p $1 -c android.intent.category.LAUNCHER 1" > /dev/null; sleep 4; }

{
log host
uname -sr; java -version 2>&1 | head -1; python3 --version; adb version | head -1
log internet
curl -sS -o /dev/null -w 'pypi %{http_code}\n' --max-time 8 https://pypi.org/simple/ || echo 'pypi unreachable'
log device
for p in ro.product.manufacturer ro.product.model ro.build.version.release ro.build.version.sdk \
         ro.build.version.oneui ro.build.display.id persist.sys.locale ro.boot.flash.locked; do
    echo "$p=$(S getprop $p)"
done
log prepare-screen
S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard; S svc power stayon usb
S settings put global stay_on_while_plugged_in 7
echo "stay_on=$(S settings get global stay_on_while_plugged_in)"
S dumpsys power | grep -E 'mWakefulness=|mIsPowered=|mPlugType=|mStayOn=' | head -5
log battery
S dumpsys battery | head -14
log deviceidle
S dumpsys deviceidle | grep -E 'mState=|mLightState=|mForceIdle=|mDeepEnabled=|mLightEnabled=' | head -6
log freezer-config
echo "use_freezer=$(S device_config get activity_manager_native_boot use_freezer)"
S dumpsys activity settings | grep -iE 'freez' | head -8
S cat /sys/fs/cgroup/cgroup.controllers
S ls /sys/fs/cgroup | head -12
log am-commands
S cmd activity help | grep -E '^ +(kill|kill-all|crash|freeze|unfreeze|stop-app|force-stop|make-uid-idle|set-inactive|get-standby-bucket|set-standby-bucket|send-trim-memory)\b'
} > "$OUT/env.txt" 2>&1

{
log install
for apk in runtime/assets/com.fsck.k9_39046.apk runtime/assets/at.bitfire.davdroid_405210002.apk runtime/assets/ws.xsoh.etar_57.apk; do
    echo "$apk: $(timeout 180 adb -s "$SERIAL" install -r -g "$apk" 2>&1 | tail -1)"
done
} > "$OUT/install.txt" 2>&1

{
log "K-9 foreground then background, sampled every 5 s for 60 s"
launch $K9
proc $K9 foreground
S input keyevent KEYCODE_HOME
for i in $(seq 1 12); do sleep 5; proc $K9 "background+$((i * 5))s"; done

log "kill methods without root, K-9 in background"
pid=$(S pidof $K9); echo "kill -9 as shell: $(S kill -9 "$pid")"; sleep 1; echo "after kill -9: $(alive $K9)"
S am kill $K9; sleep 2; echo "after am kill: $(alive $K9)"
launch $K9; S input keyevent KEYCODE_HOME; sleep 3
echo "am crash: $(S am crash $K9 | head -2)"; sleep 3; echo "after am crash: $(alive $K9)"
launch $K9; S input keyevent KEYCODE_HOME; sleep 3
echo "am stop-app: $(S am stop-app $K9 | head -2)"; sleep 2; echo "after am stop-app: $(alive $K9)"
launch $K9; S input keyevent KEYCODE_HOME; sleep 3
S am force-stop $K9; sleep 2; echo "after am force-stop: $(alive $K9)"
launch $K9; S input keyevent KEYCODE_HOME; sleep 3
echo "am freeze: $(S am freeze $K9 | head -2)"; sleep 2; proc $K9 after-am-freeze
echo "am unfreeze: $(S am unfreeze $K9 | head -2)"

log "DAVx5 foreground then background"
launch $DAV
proc $DAV foreground
S input keyevent KEYCODE_HOME
for i in 1 2 3 4; do sleep 5; proc $DAV "background+$((i * 5))s"; done
S dumpsys jobscheduler | grep -F "$DAV" | head -8

log "forced deep Doze, screen off, simulated unplug"
S dumpsys battery unplug
S input keyevent KEYCODE_SLEEP; sleep 2
echo "force-idle: $(S dumpsys deviceidle force-idle deep)"
echo "deep state: $(S dumpsys deviceidle get deep) light state: $(S dumpsys deviceidle get light)"
proc $K9 in-doze
proc $DAV in-doze
sleep 20
echo "deep state after 20 s: $(S dumpsys deviceidle get deep)"
S dumpsys deviceidle unforce; S dumpsys battery reset; S input keyevent KEYCODE_WAKEUP; S wm dismiss-keyguard
echo "after exit: deep $(S dumpsys deviceidle get deep), $(S dumpsys battery | grep -E 'USB powered|AC powered' | tr '\n' ' ')"
} > "$OUT/process.txt" 2>&1
echo "probe done"

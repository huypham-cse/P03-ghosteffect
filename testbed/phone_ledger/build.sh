#!/bin/sh
# Build the phone ledger benchmark APK without Gradle (b-log 19/11, TN3): javac, d8, aapt2, zipalign, apksigner
# from the pinned SDK in runtime/android-sdk (build-tools 33.0.2, platform android-33). Output: build/ledgerbench.apk.
# The signing key is a throwaway debug key generated into build/ (ignored by git); the APK only runs an instrumentation.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SDK="$ROOT/runtime/android-sdk"
BT="$SDK/build-tools/33.0.2"
JAR="$SDK/platforms/android-33/android.jar"
OUT="$HERE/build"
rm -rf "$OUT" && mkdir -p "$OUT/classes" "$OUT/dex"
javac -source 8 -target 8 -Xlint:-options -bootclasspath "$JAR" -d "$OUT/classes" \
    "$HERE/src/org/ghosteffect/ledgerbench/Bench.java"
java -cp "$BT/lib/d8.jar" com.android.tools.r8.D8 --release --min-api 28 --lib "$JAR" --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')
"$BT/aapt2.exe" link -o "$OUT/base.apk" -I "$JAR" --manifest "$HERE/AndroidManifest.xml" \
    --min-sdk-version 28 --target-sdk-version 33 --version-code 1 --version-name 1.0
python -c "import sys, zipfile; z = zipfile.ZipFile(sys.argv[1], 'a'); z.write(sys.argv[2], 'classes.dex'); z.close()" \
    "$OUT/base.apk" "$OUT/dex/classes.dex"
"$BT/zipalign.exe" -f 4 "$OUT/base.apk" "$OUT/aligned.apk"
keytool -genkeypair -keystore "$OUT/debug.jks" -storepass android -keypass android -alias debug -keyalg RSA \
    -keysize 2048 -validity 3650 -dname "CN=ledgerbench" > /dev/null 2>&1
java -jar "$BT/lib/apksigner.jar" sign --ks "$OUT/debug.jks" --ks-pass pass:android --key-pass pass:android \
    --out "$OUT/ledgerbench.apk" "$OUT/aligned.apk"
java -jar "$BT/lib/apksigner.jar" verify "$OUT/ledgerbench.apk"
sha256sum "$OUT/ledgerbench.apk"

package org.ghosteffect.ledgerbench;

import android.app.Instrumentation;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Build;
import android.os.Bundle;
import android.os.SystemClock;
import java.io.File;
import java.io.FileOutputStream;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * The write-ahead effect ledger of artifact/scripts/ledger.py on the phone's own SQLite (b-log 19/11, TN3).
 *
 * Modes (am instrument -e mode ...):
 *  latency: n PLANNED rows, each followed by a timed issue() in its own BEGIN IMMEDIATE transaction
 *           (WAL, synchronous=FULL by default, or -e sync NORMAL); p50/p95 in ms and bytes per effect after
 *           wal_checkpoint(TRUNCATE), as bench_ledger.latency() does on the host.
 *  writer:  loops plan, issue (durable), then appends "TAP id" to a separate file (the external side effect),
 *           then settles; started without -w and killed by the harness (am force-stop sends SIGKILL).
 *  verify:  after a kill, every tapped id must be ISSUED or COMMITTED in the ledger; then the files are removed.
 * Files live in the app's private storage (getFilesDir), where an on-device ledger would live.
 */
public class Bench extends Instrumentation {
    private Bundle args;

    @Override
    public void onCreate(Bundle arguments) {
        args = arguments == null ? new Bundle() : arguments;
        super.onCreate(arguments);
        start();
    }

    @Override
    public void onStart() {
        Bundle out = new Bundle();
        int code = 0;
        try {
            String mode = args.getString("mode", "latency");
            if (mode.equals("latency")) {
                latency(out);
            } else if (mode.equals("writer")) {
                writer();
            } else if (mode.equals("verify")) {
                verify(out);
            } else {
                throw new IllegalArgumentException("unknown mode " + mode);
            }
        } catch (Throwable t) {
            out.putString("error", t.getClass().getName() + ": " + t.getMessage());
            code = 1;
        }
        environment(out);
        finish(code, out);
    }

    private File dir() {
        return getTargetContext().getFilesDir();
    }

    private SQLiteDatabase open(File db, String sync) {
        SQLiteDatabase d;
        if (Build.VERSION.SDK_INT >= 30) {
            // TN3b (b-log 21/11): set the mode through OpenParams so that every pooled WAL connection, including the
            // primary one that writes, uses it. A bare PRAGMA may land on one connection only.
            d = SQLiteDatabase.openDatabase(db, new SQLiteDatabase.OpenParams.Builder()
                    .addOpenFlags(SQLiteDatabase.CREATE_IF_NECESSARY | SQLiteDatabase.ENABLE_WRITE_AHEAD_LOGGING)
                    .setSynchronousMode(sync).build());
        } else {
            d = SQLiteDatabase.openOrCreateDatabase(db, null);
            d.enableWriteAheadLogging();
            query1(d, "PRAGMA synchronous=" + sync);
        }
        d.execSQL("CREATE TABLE IF NOT EXISTS effects(id TEXT PRIMARY KEY, workflow TEXT, step INTEGER, app TEXT, "
                + "descr TEXT, nonce TEXT, attempt INTEGER, state TEXT, digest TEXT, t_issued REAL, t_updated REAL)");
        d.execSQL("CREATE INDEX IF NOT EXISTS effects_state ON effects(state)");
        return d;
    }

    private static String query1(SQLiteDatabase d, String sql) {
        Cursor c = d.rawQuery(sql, null);
        try {
            return c.moveToFirst() && c.getColumnCount() > 0 ? c.getString(0) : null;
        } finally {
            c.close();
        }
    }

    private static void plan(SQLiteDatabase d, String id, int step, String digest) {
        double now = System.currentTimeMillis() / 1000.0;
        d.beginTransactionNonExclusive();   // BEGIN IMMEDIATE, as ledger.py
        try {
            d.execSQL("INSERT INTO effects VALUES(?,?,?,?,?,?,?,?,?,?,?)", new Object[]{id, "wf", step,
                    "org.example.app", "transfer 1200 to Alex", "gx:7K2Q9F", 0, "PLANNED", digest, null, now});
            d.setTransactionSuccessful();
        } finally {
            d.endTransaction();
        }
    }

    private static void issue(SQLiteDatabase d, String id) {
        double now = System.currentTimeMillis() / 1000.0;
        d.beginTransactionNonExclusive();
        try {
            String state = null;
            Cursor c = d.rawQuery("SELECT state FROM effects WHERE id=?", new String[]{id});
            try {
                if (c.moveToFirst()) state = c.getString(0);
            } finally {
                c.close();
            }
            if (!"PLANNED".equals(state) && !"ABSENT".equals(state)) {
                throw new IllegalStateException("cannot issue " + id + " from " + state);
            }
            d.execSQL("UPDATE effects SET state='ISSUED', attempt=attempt+1, t_issued=COALESCE(t_issued, ?), "
                    + "t_updated=? WHERE id=?", new Object[]{now, now, id});
            d.setTransactionSuccessful();
        } finally {
            d.endTransaction();
        }
    }

    private static void settle(SQLiteDatabase d, String id) {
        d.beginTransactionNonExclusive();
        try {
            d.execSQL("UPDATE effects SET state='COMMITTED', t_updated=? WHERE id=?",
                    new Object[]{System.currentTimeMillis() / 1000.0, id});
            d.setTransactionSuccessful();
        } finally {
            d.endTransaction();
        }
    }

    private static double pct(double[] xs, double q) {
        double[] s = xs.clone();
        Arrays.sort(s);
        return s[Math.min(s.length - 1, (int) (q * s.length))];
    }

    private static long bytes(File db) {
        long total = 0;
        for (String suffix : new String[]{"", "-wal", "-shm"}) {
            File f = new File(db.getPath() + suffix);
            if (f.exists()) total += f.length();
        }
        return total;
    }

    private void latency(Bundle out) {
        int n = Integer.parseInt(args.getString("n", "2000"));
        String sync = args.getString("sync", "FULL");
        File db = new File(dir(), "latency.db");
        SQLiteDatabase.deleteDatabase(db);
        SQLiteDatabase d = open(db, sync);
        StringBuilder digest = new StringBuilder();
        for (int i = 0; i < 64; i++) digest.append('x');
        double[] ms = new double[n];
        for (int i = 0; i < n; i++) {
            plan(d, "e" + i, i, digest.toString());
            long t = SystemClock.elapsedRealtimeNanos();
            issue(d, "e" + i);
            ms[i] = (SystemClock.elapsedRealtimeNanos() - t) / 1e6;
        }
        out.putString("journal_mode", query1(d, "PRAGMA journal_mode"));
        out.putString("synchronous", query1(d, "PRAGMA synchronous"));   // any pooled connection
        d.beginTransactionNonExclusive();   // inside a transaction the session holds the primary (writing) connection
        try {
            out.putString("synchronous_writer", query1(d, "PRAGMA synchronous"));
        } finally {
            d.endTransaction();
        }
        out.putString("open_path", Build.VERSION.SDK_INT >= 30 ? "OpenParams" : "pragma");
        out.putString("sqlite_version", query1(d, "SELECT sqlite_version()"));
        query1(d, "PRAGMA wal_checkpoint(TRUNCATE)");
        d.close();
        out.putString("n", String.valueOf(n));
        out.putString("sync_requested", sync);
        out.putString("issue_p50_ms", String.format("%.3f", pct(ms, 0.5)));
        out.putString("issue_p95_ms", String.format("%.3f", pct(ms, 0.95)));
        out.putString("issue_max_ms", String.format("%.3f", pct(ms, 1.0)));
        out.putString("bytes_per_effect", String.valueOf(Math.round(bytes(db) / (double) n)));
        SQLiteDatabase.deleteDatabase(db);
    }

    private void writer() throws Exception {
        File db = new File(dir(), "crash.db");
        File tap = new File(dir(), "tap.log");
        File started = new File(getTargetContext().getExternalFilesDir(null), "started");
        SQLiteDatabase d = open(db, "FULL");
        FileOutputStream log = new FileOutputStream(tap, true);
        for (int i = 0; ; i++) {
            String id = "e" + i;
            plan(d, id, i, "");
            issue(d, id);
            log.write(("TAP " + id + "\n").getBytes("UTF-8"));   // the commit tap: an external side effect
            if (i == 0) {
                started.createNewFile();   // the harness starts its random kill window here (first observed tap)
            }
            settle(d, id);
        }
    }

    private void verify(Bundle out) throws Exception {
        File db = new File(dir(), "crash.db");
        File tap = new File(dir(), "tap.log");
        List<String> tapped = new ArrayList<String>();
        if (tap.exists()) {
            BufferedReader r = new BufferedReader(new FileReader(tap));
            try {
                for (String line; (line = r.readLine()) != null; ) {
                    String[] parts = line.trim().split(" ");
                    if (parts.length == 2) tapped.add(parts[1]);   // a torn last line is not a completed tap
                }
            } finally {
                r.close();
            }
        }
        int violations = 0, candidates = 0;
        if (db.exists()) {
            SQLiteDatabase d = SQLiteDatabase.openDatabase(db.getPath(), null, SQLiteDatabase.OPEN_READWRITE);
            Set<String> ok = new HashSet<String>();
            Cursor c = d.rawQuery("SELECT id, state FROM effects", null);
            try {
                while (c.moveToNext()) {
                    String s = c.getString(1);
                    if (s.equals("ISSUED") || s.equals("COMMITTED")) ok.add(c.getString(0));
                    if (s.equals("ISSUED")) candidates++;
                }
            } finally {
                c.close();
            }
            d.close();
            for (String id : tapped) if (!ok.contains(id)) violations++;
        }
        out.putString("db_existed", String.valueOf(db.exists()));
        out.putString("taps_checked", String.valueOf(tapped.size()));
        out.putString("invariant_violations", String.valueOf(violations));
        out.putString("ghost_candidates", String.valueOf(candidates));
        SQLiteDatabase.deleteDatabase(db);
        tap.delete();
        new File(getTargetContext().getExternalFilesDir(null), "started").delete();
    }

    private void environment(Bundle out) {
        out.putString("device", Build.MANUFACTURER + " " + Build.MODEL);
        out.putString("android_release", Build.VERSION.RELEASE);
        out.putString("sdk_int", String.valueOf(Build.VERSION.SDK_INT));
        out.putString("build_display", Build.DISPLAY);
    }
}

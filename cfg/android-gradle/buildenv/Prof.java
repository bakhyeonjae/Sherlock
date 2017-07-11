package com.sec.android.app.camera;

import android.util.Log;

public class Prof {
    private static final String TAG="SHERLOCK/PROFILING/BEHAVIOUR";

    public static void entry(String message) {
        Log.i(TAG,"[entry] " + message);
    }

    public static void exit(String message) {
        Log.i(TAG,"[exit] " + message);
    }
}

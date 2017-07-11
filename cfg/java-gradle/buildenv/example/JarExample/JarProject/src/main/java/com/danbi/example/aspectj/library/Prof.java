package com.danbi.example.aspectj.library;

import java.util.Date;
import java.text.SimpleDateFormat;

public class Prof {
    private static final String TAG="SHERLOCK/PROFILING/BEHAVIOUR";

    public static void entry(String message) {
        System.out.println(TAG + " " + getCurrentTime() + getCurrentThreadID() + " [entry] " + message);
    }

    public static void exit(String message) {
        System.out.println(TAG + " " + getCurrentTime() + getCurrentThreadID() + " [exit] " + message);
    }

    private static String getCurrentTime() {
        
        long now = System.currentTimeMillis();
        java.util.Date date = new java.util.Date(now);
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS ");
        String timeString = format.format(date);

        return timeString;
    }

    private static long getCurrentThreadID() {
        Thread currentThread = Thread.currentThread();
        return currentThread.getId();
    }
}

package com.sec.android.app.camera;

import org.aspectj.lang.Signature;

public aspect AutoLog {
    pointcut publicMethods() : execution(public * *..*(..));
    pointcut protectedMethods() : execution(protected * *..*(..));
    pointcut privateMethods() : execution(private * *..*(..));
    pointcut allMethods() : execution(* *..*(..));
    pointcut logObjectCalls() : execution(* Prof.*(..));
    pointcut loggableCalls() : allMethods() && ! logObjectCalls();

    before() : loggableCalls() {
        Signature sig = thisJoinPoint.getSignature();
        String str = sig.toLongString();

        Object[] paramValues = thisJoinPoint.getArgs();
        if (paramValues.length != 0)
            str += " [args] ";

        for (Object object:paramValues) {
            if (null != object)
                str += object.toString() + ",,";
        }

        Prof.entry(str);
    }

    after() returning(Object objectRet) : loggableCalls() {
        Signature sig = thisJoinPoint.getSignature();
        String str = sig.toLongString();
        if (null != objectRet){
            str += " [returns] ";
            str += objectRet.toString();
        }
        Prof.exit(str);
    }
}

import re
import datetime
import threading
import inspect

def convertListToStr(string):
    if isinstance(string, list):
        ret = "["
        if len(string) > 10:
            ret += "..."
        else:
            for s in string:
                ret += convertListToStr(s) + ','
            ret += "]"
    elif isinstance(string, dict):
        if len(string) > 10:
            ret = "{...}"
        else:
            ret = str(string)
    else:
        ret = str(string)
    return ret

class Aspecter(type):
    aspect_rules = []
    LOG_TAG = 'SHERLOCK/PROFILING/BEHAVIOUR'

    def __new__(cls, name, bases, dict):
        module_name = "%s.%s" % (dict['__module__'],name)
        for key, value in dict.items():
            if hasattr(value, "__call__") and key != "__metaclass__":
                dict[key] = Aspecter.wrap_method(value,module_name)
            return type.__new__(cls, name, bases, dict)

    @classmethod
    def register(cls, name_pattern="", in_objects=(), out_objects=()):
        rule = {"name_pattern": name_pattern, "in_objects": in_objects, "out_objects": out_objects}
        cls.aspect_rules.append(rule)

    @classmethod
    def wrap_method(cls, method, moduleName):
        def call(*args, **kw):
            day = datetime.date.today()
            t = datetime.datetime.now().time()
            tid = threading.current_thread().ident
            arg_str = '[args]'
            for idx in range(1, len(args)):
                arg_str += convertListToStr(args[idx]) + ',,'
            print("%s %s %s %d [entry] void %s.%s() %s" % (cls.LOG_TAG, day.isoformat(), t.isoformat(), tid, moduleName, method.__name__, arg_str))
            results = method(*args, **kw)
            t = datetime.datetime.now().time()
            ret_str = '[ret]'
            if results:
                for idx in range(1,len(results)):
                    ret_str += convertListToStr(result[idx]) + ',,'
            print("%s %s %s %d [exit] void %s.%s() %s" % (cls.LOG_TAG, day.isoformat(), t.isoformat(), tid, method.__module__, method.__name__, ret_str))
            return results
        return call

def loggable(method):
    def wrapAndCall(*args, **kw):
        day = datetime.date.today()
        t = datetime.datetime.now().time()
        tid = threading.current_thread().ident
        arg_str = '[args]'
        for idx in range(0,len(args)):
            arg_str += convertListToStr(args[idx]) + ',,'
        print("%s %s %s %d [entry] void %s.%s() %s" % (Aspecter.LOG_TAG, day.isoformat(), t.isoformat(), tid, method.__module__,method.__name__,arg_str))
        results = method(*args, **kw)
        t = datetime.datetime.now().time()
        ret_str = '[ret]'
        if results:
            for idx in range(0,len(results)):
                ret_str += convertListToStr(results[idx]) + ',,'
        print("%s %s %s %d [exit] void %s.%s() %s" % (Aspecter.LOG_TAG, day.isoformat(), t.isoformat(), tid, method.__module__,method.__name__,ret_str))
        return results
    return wrapAndCall

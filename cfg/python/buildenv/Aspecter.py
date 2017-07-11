import re
import datetime

class Aspecter(type):
    aspect_rules = []
    LOG_TAG = 'SHERLOCK/PROFILING/BEHAVIOUR'

    def __new__(cls, name, bases, dict):
        for key, value in dict.items():
            if hasattr(value, "__call__") and key != "__metaclass__":
                dict[key] = Aspecter.wrap_method(value)
        return type.__new__(cls, name, bases, dict)

    @classmethod
    def register(cls, name_pattern="", in_objects=(), out_objects=()):
        rule = {"name_pattern": name_pattern, "in_objects": in_objects, "out_objects": out_objects}
        cls.aspect_rules.append(rule)

    @classmethod
    def wrap_method(cls, method):
        def call(*args, **kw):
            day = datetime.date.today()
            t = datetime.datetime.now().time()
            arg_str = '[args]' if len(args) > 1 else None
            for idx in range(1,len(args)):
                arg_str += args[idx] + ',,'
            print("%s %s %s [entry] %s %s" % (cls.LOG_TAG,day.isoformat(),t.isoformat(),method.__name__,arg_str))
            results = method(*args, **kw)
            print("%s %s %s [exit] %s" % (cls.LOG_TAG,day.isoformat(),t.isoformat(),method.__name__))
            return results
        return call

def loggable(method):
    def wrapAndCall(*args, **kw):
        day = datetime.date.today()
        t = datetime.datetime.now().time()
        arg_str = '[args]' if len(args) > 0 else None
        for idx in range(0,len(args)):
            arg_str += args[idx] + ',,'
        print("%s %s %s [entry] %s %s" % (Aspecter.LOG_TAG, day.isoformat(), t.isoformat(), method.__name__, arg_str))
        result = method(*args, **kw)
        print("%s %s %s [exit] %s" % (Aspecter.LOG_TAG, day.isoformat(), t.isoformat(), method.__new__))
        return results
    return wrapAndCall

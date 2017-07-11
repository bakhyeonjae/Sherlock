import re

def argumentsToAttributes(method):
    #argumentNames = method.func_code.co_varnames[1:]   # python 2
    argumentNames = method.__code__.co_varnames[1:]   # python 2

    # Generate a dictionary of default values:
    defaultsDict = {}
    #defaults = method.func_defaults if method.func_defaults else ()   #python2
    defaults = method.__defaults__ if method.__defaults__ else ()    #python3
    for i, default in enumerate(defaults, start = len(argumentNames) - len(defaults)):
        defaultsDict[argumentNames[i]] = default

    def newMethod(self, *args, **kwargs):
        # Use the positional arguments.
        for name, value in zip(argumentNames, args):
            setattr(self, name, value)

        # Add the key word arguments. If anything is missing, use the default.
        for name in argumentNames[len(args):]:
            setattr(self, name, kwargs.get(name, defaultsDict[name]))

        # Run whatever else the method needs to do.
        method(self, *args, **kwargs)

    return newMethod

def calcCoordinate(v):
    """
    calcCoordinate multiply 'v' with message distance.
    'Message distance' is size for plotting a message on life-line in pixels.
    Now, it's defined as 35.
    This method is for performance increase
    """
    # Multiply 35 on the given value - v
    return (v<<5) + (v<<1) + v

def calcTimeConsumed(begin, end):
    if None == end:
        return -1

    begin_str = begin.split(":")
    begin_h   = int(begin_str[0])
    begin_m   = int(begin_str[1])
    begin_s   = int(float(begin_str[2])*1000)

    end_str = end.split(":")
    end_h   = int(end_str[0])
    end_m   = int(end_str[1])
    end_s   = int(float(end_str[2])*1000)

    begin_in_msec = begin_h*3600000 + begin_m*60000 + begin_s
    end_in_msec   = end_h*3600000 + end_m*60000 + end_s

    difference = end_in_msec - begin_in_msec if end_in_msec >= begin_in_msec else begin_in_msec+24*60*60*1000

    return difference

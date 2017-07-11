"""
Kitchen is a main controller class of SOHOJUNG.
This class controls all the user events and drives business logic.
Model part of SOHOJUNG is called office.

author: Bak Hyeonjae
"""
import threading
import time
from threading import Timer, Lock
from copy import deepcopy
import Stack
import re
import sys
import const
import io

class Kitchen(threading.Thread):

    input_stream = None
    flagTerminate = False
    STR_CLASS_SPLITTER = '\\.|\\*|\\:\\:'
   
    def __init__(self,mode,fileArg,cfgArg):
        threading.Thread.__init__(self)
       
        self.mode = mode
        self.argFile = fileArg
        self.cfgFile = cfgArg
        self.mutex = Lock()

        self.reset()

        const.STATE_INTERACTIVE_IDLE = 0
        const.STATE_INTERACTIVE_CAPTURING = 1
        const.STATE_INTERACTIVE_PROCESSING = 2
        const.STATE_INTERACTIVE_ACTIVE = 3
        const.STATE_INTERACTIVE_RESET = 4
        self.stateInteractive = const.STATE_INTERACTIVE_IDLE

        if const.mode_interactive == self.mode:
            self.input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')

    def reset(self):
        self.lifeLine = []
        self.callStack = [] #Stack.Stack()
        self.threads = []
        self.cnt = 0

    def connectView(self,view):
        self.view = view    # set restaurant(view) component
        
    def connectToolBox(self,toolBox):
        self.toolBox = toolBox

    def terminate(self):
        self.flagTerminate = True
        self.mutex.release()
    
    def run(self):
        while True:
            self.mutex.acquire()
            if self.flagTerminate:
                break

            self.loadData()
            self.mutex.release()
            self.setInteractiveModeState(const.STATE_INTERACTIVE_ACTIVE)

    def loadData(self):

        self.lifeLine.append("start")
        self.view.addLifeline("start")

        input_dat = []

        if const.mode_interactive == self.mode:
            for idx, line in enumerate(self.input_stream):
                if const.STATE_INTERACTIVE_RESET == self.stateInteractive:
                    self.setInteractiveModeState(const.STATE_INTERACTIVE_CAPTURING)
                if const.STATE_INTERACTIVE_IDLE == self.stateInteractive:
                    continue
                elif const.STATE_INTERACTIVE_PROCESSING == self.stateInteractive:
                    break
                input_dat.append(line)
        elif const.mode_batch == self.mode:
            input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='ignore')
            for idx, line in enumerate(input_stream):
                input_dat.append(line)
        elif const.mode_file == self.mode:
            file_in = open(self.argFile,"r", encoding='utf-8', errors='ignore')
            for idx, line in enumerate(file_in):
                input_dat.append(line)

        idx_for_remove = []
        for idx, line in list(reversed(list(enumerate(input_dat)))):
            match_flag = False
            if '[exit]' in line:
                for _i in reversed(range(0,idx)):
                    if '[entry]' in input_dat[_i]:
                        exit_str = line.split()
                        exit_method_name = ''
                        for _j in range(8,len(exit_str)):
                            exit_method_name += exit_str[_j]

                        entry_str = input_dat[_i].split()
                        entry_method_name = ''
                        for _j in range(8,len(entry_str)):
                            entry_method_name += entry_str[_j]

                        entry_method_name_arg_removed = entry_method_name.split("[args]")[0]
                        entry_method_name_arg_ret_removed = entry_method_name_arg_removed.split("[returns]")[0]
                        exit_method_name_arg_removed = exit_method_name.split("[args]")[0]
                        exit_method_name_arg_ret_removed = exit_method_name_arg_removed.split("[returns]")[0]

                        if entry_method_name_arg_ret_removed == exit_method_name_arg_ret_removed:
                            match_flag = True
                            break

                if False == match_flag:
                    print("REMOVE the line !!! -> %d" % idx)
                    idx_for_remove.append(idx)

        for _i in idx_for_remove:
            del input_dat[_i]

        cfg_file_in = open(self.cfgFile,"r", encoding='utf-8', errors='ignore')
        
        cfg_time_index = 0
        cfg_thread_index = 0
        cfg_flowtype_index = 0
        cfg_methodname_index = 0
        cfg_ignore_str = None
        cfg_arg_seperator = None
        cfg_filter_tag = None

        for line in cfg_file_in:
            if '[time]' in line:
                str = line.split('[time]')
                cfg_time_index = int(str[1])
            elif '[thread]' in line:
                str = line.split('[thread]')
                cfg_thread_index = int(str[1])
            elif '[flowtype]' in line:
                str = line.split('[flowtype]')
                cfg_flowtype_index = int(str[1])
            elif '[methodname]' in line:
                str = line.split('[methodname]')
                cfg_methodname_index = int(str[1])
            elif '[ignore]' in line:
                str = line.split('[ignore]')
                cfg_ignore_str = str[1].replace(' ','').replace('\n','').split(',')
            elif '[argseperator]' in line:
                str = line.split('[argseperator]')
                cfg_arg_seperator = str[1].replace(' ','').replace('\n','')
            elif '[filtertag]' in line:
                str = line.split('[filtertag]')
                cfg_filter_tag = str[1].replace(' ','').replace('\n','')

        cfg_file_in.close()

        filter_str = "(.*)%s(.*)" % (cfg_filter_tag)
        index = 0        
        for idx, line in enumerate(input_dat):
            if re.match(filter_str,line):
                str_list = line[:]
                for word in cfg_ignore_str:
                    str_list = str_list.replace(word,'')
                str_list = str_list.split()

                if len(str_list) < max(cfg_time_index,cfg_thread_index,cfg_flowtype_index,cfg_methodname_index):
                    print("input line has some errors : %s"%line)
                    continue
                
                if '[entry]' not in line and '[exit]' not in line:
                    print("input line has some errors : %s" % line)
                    continue

                event_time = str_list[cfg_time_index]
                thread_id = str_list[cfg_thread_index]
                flow_type = str_list[cfg_flowtype_index]
                method_name_index = cfg_methodname_index

                package_method_name = ''
                for _i in range(method_name_index,len(str_list)):
                    package_method_name += str_list[_i] + ' '

                org_line = line[:]
                arguments_str = org_line.split("[args]")[1] if "[args]" in org_line else None
                return_str = org_line.split("[returns]")[1] if "[returns]" in org_line else None
                arg_removed = package_method_name.split("[args]")[0]
                ret_removed = arg_removed.split("[returns]")[0]
                parameter_removed = package_method_name.split("(")[0]
                inside_parenthesis = package_method_name.split("(")[1].split(")")[0].replace(' ','')
                parameters = None
                if '' != inside_parenthesis:
                    parameters = inside_parenthesis.split(',')
                return_type_removed = ".".join(list(parameter_removed.split(' '))[1:])
                method_name = list(reversed(re.split(self.STR_CLASS_SPLITTER,return_type_removed)))[0]
                package_name = ".".join(list(reversed(list(reversed(re.split(self.STR_CLASS_SPLITTER,return_type_removed)))[1:])))

                class_name = package_name
                if class_name == '':
                    class_name = 'Global'

                if not (thread_id in self.threads):
                    self.threads.append(thread_id)
                    stack = Stack.Stack()
                    stack.push({'class':"start", 'message':""})
                    self.callStack.append(stack)

                if not (class_name in self.lifeLine):
                    self.view.addLifeline(class_name)
                    self.lifeLine.append(class_name)

                thread_index = self.threads.index(thread_id)

                if flow_type == "[entry]":
                    self.view.sendSignal(self.callStack[thread_index].peek(),class_name,method_name,thread_index,event_time,index+1,self.callStack[thread_index],arguments_str.split(cfg_arg_seperator) if arguments_str else None,parameters)
                    self.callStack[thread_index].push({'class':class_name, 'message':method_name})

                if flow_type == "[exit]":
                    self.view.completeTask(class_name,method_name,1,event_time,index+1,self.callStack[thread_index].depth('compareClass'),return_str.split(cfg_arg_seperator) if return_str else None)
                    self.callStack[thread_index].pop()

                index += 1

            del line
            self.cnt = index

        self.view.refreshData(self.cnt)
        self.view.setDrawingAvailable()
        self.toolBox.setAvailable(self.threads)
        
    def activateHide(self,flag):
        pass

    def resetAllLifelines(self):
        pass

    def activateCapture(self,flag):
        if const.STATE_INTERACTIVE_IDLE == self.stateInteractive or const.STATE_INTERACTIVE_RESET == self.stateInteractive:
            self.setInteractiveModeState(const.STATE_INTERACTIVE_CAPTURING)
        elif const.STATE_INTERACTIVE_CAPTURING == self.stateInteractive:
            self.setInteractiveModeState(const.STATE_INTERACTIVE_PROCESSING)
        elif const.STATE_INTERACTIVE_ACTIVE == self.stateInteractive:
            self.setInteractiveModeState(const.STATE_INTERACTIVE_RESET)

    def setInteractiveModeState(self,state):
        
        self.toolBox.notifyInteractiveStateChanged(state)

        if const.STATE_INTERACTIVE_RESET == state:
            if const.STATE_INTERACTIVE_ACTIVE != self.stateInteractive:
                pass # throw exception
            self.view.reset()
            self.reset()
            self.stateInteractive = const.STATE_INTERACTIVE_RESET
            self.mutex.release()

        if const.STATE_INTERACTIVE_ACTIVE == state:
            if const.STATE_INTERACTIVE_PROCESSING != self.stateInteractive:
                pass # throw exception
            self.stateInteractive = const.STATE_INTERACTIVE_ACTIVE
            self.mutex.acquire()

        if const.STATE_INTERACTIVE_PROCESSING == state:
            if const.STATE_INTERACTIVE_CAPTURING != self.stateInteractive:
                pass # throw exception
            self.stateInteractive = const.STATE_INTERACTIVE_PROCESSING

        if const.STATE_INTERACTIVE_CAPTURING == state:
            if const.STATE_INTERACTIVE_IDLE != self.stateInteractive or const.STATE_INTERACTIVE_RESET != self.stateInteractive:
                pass # throw exception
            self.stateInteractive = const.STATE_INTERACTIVE_CAPTURING

    def searchMessage(self,str):
        pass

    def moveToPrev(self):
        pass
        
    def moveToNext(self):
        pass

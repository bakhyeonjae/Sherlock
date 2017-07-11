import Aspecter

class Human(object):
    __metaclass__ = Aspecter.Aspecter

    name = None
    def __init__(self,name):
        self.name = name

    def walk(self):
        print("%s walks" % self.name)

    def run(self):
        print("%s runs" % self.name)

    def command(self, cmdType, receiver):
        if 'walk' == cmdType:
            receiver.walk()
        elif 'run' == cmdType:
            receiver.run()

Aspecter.Aspecter.register(name_pattern="^.*")


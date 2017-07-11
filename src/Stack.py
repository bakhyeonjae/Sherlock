class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)

    def depth(self,compare):
        top_item = self.items[len(self.items)-1]
        counter = 0

        for item in self.items:
            if True == eval('%s(%s,%s)'%(compare,top_item,item)):
                counter = counter + 1

        return counter

    def list(self):
        return self.items

    def setID(self,id):
        self.id = id

    def getID(self):
        return self.id

def compareClass(A,B):
    return True if A['class'] == B['class'] else False

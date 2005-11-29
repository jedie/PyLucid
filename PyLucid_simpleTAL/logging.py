class DummyLogger:
    def debug (self, *args): pass
    def info (self, *args): pass

    def warn (self, *args):
        print args

    def error (self, *args):
        print args

    def critical (self, *args):
        print args

def getLogger (*params):
    return DummyLogger()
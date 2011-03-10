# Built-in function any() was introduced in Python 2.5
try:
    any = any
except NameError:
    def any(seq):
        for x in seq:
            if x:
                return True
        return False

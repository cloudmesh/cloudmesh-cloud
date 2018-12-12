from pprint import pprint

def debugger(func):
    def function_wrapper(x):
        d= func(x)
        print("Output:", func.__name__)
        pprint(d)
    return function_wrapper

def DatabaseUpdate(func):
    def function_wrapper(x):
        d= func(x)
        print("DataBase Update:", func.__name__)
        print("Just a placeholder. Not yet implemented")
        if d is None:
            pass
        else:
            pprint(d)
    return function_wrapper

""" Example.
@debugger
def foo(x):
    return {"test": "hello"}

@DatabaseUpdate
def bar(x):
    return {"test": "hello"}
"""

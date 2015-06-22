import time

def testing() :
    time.sleep(5)
    return False

if not testing() :
    print('error')
import threading
import sys
import time
import traceback

def dump_stacks():
    time.sleep(10)
    print("Dumping stacks:")
    for th in threading.enumerate():
        print(th)
        traceback.print_stack(sys._current_frames()[th.ident])
        print("--------------------")

t = threading.Thread(target=dump_stacks)
t.daemon = True
t.start()

print("Importing app.main...")
import app.main
print("Import complete!")

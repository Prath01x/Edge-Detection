import argparse
import signal


from multiprocessing import Process, Queue

from timeout_error import TimeoutError


VERBOSE = False
TIMEOUT = 20

class colors:
    FAIL = "\033[91m" # red
    TIMEOUT = "\033[93m" # orange
    SIGNAL = "\033[93m" # orange
    PASS = "\033[92m" # green
    OK = "\033[94m" # bright blue
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    HEADER = f"{OK}{BOLD}" # bright blue + bold
    FRAME = f"{UNDERLINE}\033[53m" # underline + overline
    END = "\033[0m" # end color

def get_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--filter', type=str, metavar='<regex>', help='only execute tests matching this regex')
    argparser.add_argument('-l', '--list', action='store_true', help='only list tests, don\'t execute')
    argparser.add_argument('-nc', '--no-color', action='store_true', help='disable colored output')
    return argparser

def run_single_test(test, queue, color):
    msg = test.run_test(color=color)
    queue.put(msg)

def run_tests(args, all_tests):
    num_passed = 0
    
    color = True
    
    if args.no_color:
        color = False
    
    for t in all_tests:
        if color:
            print(f"{colors.HEADER}Running test {t.get_name()} {colors.END}")
        else:
            print(f"Running test {t.get_name()}")
    
        queue = Queue()
        p = Process(target=run_single_test, args=(t, queue, color))
        p.start()
        p.join(timeout=TIMEOUT)

        if p.is_alive():
            p.kill()
            p.join()
            
            if color:
                print(f"{colors.TIMEOUT}FAIL: Timed out after {TIMEOUT} seconds.{colors.END}")
            else:
                print(f"FAIL: Timed out after {TIMEOUT} seconds.")
            
            continue
        elif p.exitcode < 0:
            name = signal.Signals(-p.exitcode).name
            
            if color:
                msg = f"{colors.SIGNAL}SIGNAL: Received signal {name}.{colors.END}"
            else:
                msg = f"SIGNAL: Received signal {name}."
            
            print(msg)
            print()
            
            continue
            
        try:
            result = queue.get_nowait()
        except Exception as e:
            result = "error " + str(e)
        
        if result is None:
            if color:
                print(f"{colors.PASS}PASS{colors.END}")
            else:
                print("PASS")

            num_passed += 1
            
        else:
            if color:
                print(f"{colors.FAIL}FAIL:{colors.END} {result}")
            else:
                print(f"FAIL: {result}")

        print()


    if color:
        print(f"\n{colors.FRAME}{colors.HEADER}Passed {num_passed} out of {len(all_tests)} tests.{colors.END}")
    else:
        print(f"\nPassed {num_passed} out of {len(all_tests)} tests.")


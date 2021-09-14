import sys
import platform
import logging
import time
import random
import hashlib
from game_env import GameEnv
from solution import Solver

# automatic timeout handling will only be performed on Unix
if platform.system() != 'Windows':
    import signal
    WINDOWS = False
else:
    WINDOWS = True

DEBUG_MODE = False  # set to True to disable time limit checks

CRASH = 255
OVERTIME = 254

"""
Simulator script.

Run this file to evaluate the performance of the policy generated by your solver for a given input file. You may modify
this file if desired. When submitting to GradeScope, an unmodified version of this file will be used to evaluate your
code.

The return code produced by simulator is your solver's score for the testcase (multiplied by 10 and represented as an
integer).

Simulator seeds random outcomes to produce consistent policy performance between runs - if your code is deterministic
and does not exceed the time limit, simulator will always produce the a consistent score.

The simulator will automatically terminate your solver if it runs over 2x the allowed time limit for any step (on Unix
platforms only - not available on Windows). This feature can be disabled for debugging purposes by setting
DEBUG_MODE = True above.
"""


class TimeOutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeOutException


def stable_hash(x):
    return hashlib.md5(str(x).encode('utf-8')).hexdigest()


def main(arglist):
    if len(arglist) != 1:
        print("Running this file tests executes your code and evaluates the performance of the generated policy for the"
              " given input file.")
        print("Usage: simulator.py [input_filename]")
        return

    input_file = arglist[0]
    init_seed = stable_hash(input_file)
    random.seed(init_seed)
    env = GameEnv(input_file)

    # initialise solver
    if not WINDOWS and not DEBUG_MODE:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)
    try:
        solver = Solver(env)
        if not WINDOWS and not DEBUG_MODE:
            signal.alarm(0)
    except TimeOutException as e:
        logging.exception(e)
        print("/!\\ Terminated due to running over 2x time limit in solver.__init__()")
        sys.exit(OVERTIME)
    except Exception as e:
        logging.exception(e)
        print("/!\\ Terminated due to exception generated in solver.__init__()")
        sys.exit(CRASH)

    # run offline computation
    if not WINDOWS and not DEBUG_MODE:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(env.offline_time + 1))
    try:
        t0 = time.time()
        solver.plan_offline()
        t_offline = time.time() - t0
        if not WINDOWS and not DEBUG_MODE:
            signal.alarm(0)
    except TimeOutException as e:
        logging.exception(e)
        print("/!\\ Terminated due to running over 2x time limit in plan_offline()")
        sys.exit(OVERTIME)
    except Exception as e:
        logging.exception(e)
        print("/!\\ Terminated due to exception generated in plan_offline()")
        sys.exit(CRASH)

    # simulate episode
    t_online_max = 0
    terminal = False
    reward = None
    total_reward = 0
    persistent_state = env.get_init_state()
    visit_count = {persistent_state.deepcopy(): 1}
    while not terminal and total_reward > (env.reward_tgt * 2):
        # query solver to select an action
        if not WINDOWS and not DEBUG_MODE:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(env.online_time + 1))
        try:
            t0 = time.time()
            action = solver.select_action(persistent_state)
            t_online = time.time() - t0
            if not WINDOWS and not DEBUG_MODE:
                signal.alarm(0)
            if t_online > t_online_max:
                t_online_max = t_online
        except TimeOutException as e:
            logging.exception(e)
            print("/!\\ Terminated due to running over 2x time limit in select_action()")
            sys.exit(OVERTIME)
        except Exception as e:
            logging.exception(e)
            print("/!\\ Terminated due to exception generated in select_action()")
            sys.exit(CRASH)

        if action not in GameEnv.ACTIONS:
            print("/!\\ Unrecognised action selected by select_action()")
            sys.exit(CRASH)

        # simulate outcome of action
        seed = (init_seed + stable_hash(str((persistent_state.row, persistent_state.col, persistent_state.gem_status)))
                + stable_hash(visit_count[persistent_state]))
        valid, reward, persistent_state, terminal = env.perform_action(persistent_state, action, seed=seed)
        if not valid:
            print("/!\\ Invalid action selected by select_action()")
            sys.exit(CRASH)
        # updated visited state count (for de-randomisation)
        ps = persistent_state.deepcopy()
        if ps in visit_count.keys():
            visit_count[ps] += 1
        else:
            visit_count[ps] = 1
        # update episode reward
        total_reward += reward

    if reward > (-1 * env.game_over_penalty):
        print(f"Level completed with a total reward of {round(total_reward, 1)}!")
    else:
        print(f"Level ended in Game Over with a total reward of {round(total_reward, 1)}.")

    # compute score for episode
    # run time deductions
    td_offline = max(t_offline - env.offline_time, 0) / env.offline_time
    if td_offline > 0:
        print(f'Exceeded offline time limit by {round(td_offline * 100)}%')
    td_online = max(t_online_max - env.online_time, 0) / env.online_time
    if td_online > 0:
        print(f'Exceeded online time limit by {round(td_online * 100)}%')
    td = max(td_offline, td_online)
    # policy performance deductions
    pd = max(env.reward_tgt - total_reward, 0) / abs(env.reward_tgt)
    if pd > 1e-6:
        print(f'Below reward target by {round(pd * 100)}%')
    # total deduction
    total_deduction = min(td + pd, 1.0)
    score = round(5.0 * (1.0 - total_deduction), 1)
    print(f'Score for this testcase is {score} / 5.0')
    ret_code = int(round(score * 10))
    # return code is score (out of 5.0) multiplied by 10
    sys.exit(ret_code)


if __name__ == '__main__':
    main(sys.argv[1:])



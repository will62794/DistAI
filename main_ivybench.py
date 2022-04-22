import sys
import subprocess
import time
import os
import shutil

bms = [
    "tla-consensus",
    "tla-tcommit",
    "i4-lock-server",
    "ex-quorum-leader-election",
    "pyv-toy-consensus-forall",
    "tla-simple",
    "ex-lockserv-automaton",
    "tla-simpleregular",
    "pyv-sharded-kv",
    "pyv-lockserv",
    "tla-twophase",
    "i4-learning-switch",
    "ex-simple-decentralized-lock",
    "i4-two-phase-commit",
    "pyv-consensus-wo-decide",
    "pyv-consensus-forall",
    "pyv-learning-switch",
    "i4-chord-ring-maintenance",
    "pyv-sharded-kv-no-lost-keys",
    "ex-naive-consensus",
    "pyv-client-server-ae",
    "ex-simple-election",
    "pyv-toy-consensus-epr",
    "ex-toy-consensus",
    "pyv-client-server-db-ae",
    "pyv-hybrid-reliable-broadcast",
    "pyv-firewall",
    "ex-majorityset-leader-election",
    "pyv-consensus-epr",
    "mongo-logless-reconfig"
]

PROBLEM = 'leader'

MAX_TEMPLATE_INCREASE = 3

def run_benchmark(PROBLEM):
    success = False
    counterexample_count, invariant_count = 0, 0
    simulation_time, enumeration_time, refinement_time = 0, 0, 0
    if not os.path.exists('src-c/runtime'):
        os.mkdir('src-c/runtime')
    c_runtime_path = 'src-c/runtime/' + PROBLEM
    shutil.rmtree(c_runtime_path, ignore_errors=True)
    os.mkdir(c_runtime_path)
    output_path = 'outputs/{}'.format(PROBLEM)
    shutil.rmtree(output_path, ignore_errors=True)
    os.mkdir(output_path)
    result = {}
    for i in range(MAX_TEMPLATE_INCREASE):
        if i > 0:
            print('Re-simulate protocol with larger instances')
        start_time = time.time()
        subprocret = subprocess.run(['python3', 'translate.py', PROBLEM, '--num_attempt={}'.format(i)], cwd='src-py/')
        if subprocret.returncode != 0:
            print('translate.py fails to parse and translate the input Ivy file. Please use $ivy_check PROTOCOL.ivy to '
                  'check if the Ivy file has the correct syntax and grammar. If it does, the problem may come from the '
                  'limitation of DistAI, which does not support all Ivy features. Exiting...')
            return {"success": False, "parse_error": True}
        subprocess.run(['python3', '{}.py'.format(PROBLEM)], cwd='auto_samplers/', check=True)
        end_time = time.time()
        simulation_time += end_time - start_time
        if i == 0:
            subprocess.run(['./main', PROBLEM], cwd='src-c/')
        else:
            subprocess.run(['./main', PROBLEM, '--max_retry={}'.format(i)], cwd='src-c/')
        refiner_log_lines = None
        try:
            with open(c_runtime_path + '/refiner_log.txt', 'r') as refiner_log_file:
                refiner_log_lines = refiner_log_file.readlines()
        except FileNotFoundError:
            print("error, file not found:", c_runtime_path + '/refiner_log.txt')
            return {"success": False}

        for line in refiner_log_lines:
            if line.startswith('Success?'):
                if line[len('Success?') + 1:].strip() == 'Yes':
                    success = True
            elif line.startswith('Counterexamples:'):
                counterexample_count += int(line[len('Counterexamples:') + 1:].strip())
            elif line.startswith('Invariants:'):
                invariant_count = int(line[len('Invariants:') + 1:].strip())
            elif line.startswith('Enumeration time:'):
                enumeration_time += int(line[len('Enumeration time:') + 1:].strip())
            elif line.startswith('Refinement time:'):
                refinement_time += int(line[len('Refinement time:') + 1:].strip())
        if success:
            break
    if success:
        enumeration_time = enumeration_time / 1000  # convert ms to s
        refinement_time = refinement_time / 1000
        total_time = simulation_time + enumeration_time + refinement_time 

        result["duration_secs"] = int(total_time)
        result["ninvs"] = invariant_count + 1
    result["success"] = success
    return result
if __name__ == '__main__':
    bms_to_run = bms[:]
    results = []

    # Collect results.
    for ind,bm in enumerate(bms_to_run):
        msg = f"=== Running benchmark {ind+1}/{len(bms_to_run)}: '{bm}'"
        print(msg)
        sys.stdout.flush()
        result = run_benchmark(f"ivybench-{bm}")
        print(result)
        result["bmname"] = bm
        results.append(result)
    
    # Save results to CSV.
    f = open("distai_ivybench_results.csv", 'w')
    f.write("protocol,duration_secs,invsize\n")
    for r in results:
        if r["success"]:
            f.write(",".join([r["bmname"],str(r["duration_secs"]),str(r["ninvs"])]))
        elif not r["success"] and "parse_error" in r:
            f.write(",".join([r["bmname"],"error","-"]))
        else:
            # No parse error but terminated without discovering an invariant.
            f.write(",".join([r["bmname"],"fail","-"]))
        f.write("\n")
    f.close()
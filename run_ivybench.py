import subprocess,sys
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
    "pyv-consensus-epr"
]

bms_to_run = bms[:8]
results = []
for ind,bm in enumerate(bms_to_run):
    msg = f"=== Running benchmark {ind+1}/{len(bms_to_run)}: '{bm}'"
    print(msg)
    sys.stdout.flush()
    cmd = f"python3 main.py ivybench-{bm}"
    ret = subprocess.run(cmd, shell=True, capture_output=True)

    stdout = ret.stdout.decode("utf-8")
    stderr = ret.stderr.decode("utf-8")
    print(stdout)
    print("ret stderr", ret.stderr)
    print("ret stderr", bool(ret.stderr))
    result = {"bmname": bm}

    if "fails to parse" in stdout:
        result["duration_secs"]="error"
        result["ninvs"]=None
        results.append(result)
        continue

    outlines = stdout.splitlines()
    for line in outlines:
        # print(str(line))
        # DistInv runtime: 26.447s
        if "DistInv runtime" in line:
            print(line.split(":")[1].strip().replace("s", ""))
            runtime_secs = int(float(line.split(":")[1].strip().replace("s", "")))
            result["duration_secs"]=runtime_secs
        # Invariants: 66
        if "Invariants" in line and line.startswith("Invariants"):
            num_invs = int(line.split(":")[1].strip()) + 1
            result["ninvs"]=num_invs

    # print(ret.stdout)
    if ret.stderr:
        errlines = stderr.splitlines()
        for line in errlines:
            print(str(line))
        result["duration_secs"]="error"
        result["ninvs"]=None
    results.append(result)
for r in results:
    print(r)

f = open("distai_ivybench_results.csv", 'w')
f.write("bm,duration_secs,ninvs\n")
for r in results:
    f.write(",".join([r["bmname"],str(r["duration_secs"]),str(r["ninvs"])]))
    f.write("\n")
f.close()
    # retlines = ret.stdout.splitlines()
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

f = open("distai_ivybench_log.txt", 'w')
bms_to_run = bms
for ind,bm in enumerate(bms_to_run):
    msg = f"=== Running benchmark {ind+1}/{len(bms_to_run)}: '{bm}'"
    print(msg)
    sys.stdout.flush()
    cmd = f"python3 main.py ivybench-{bm}"
    ret = subprocess.run(cmd, shell=True)
    # print(ret.stdout)
    # print(ret.stderr)
    # retlines = ret.stdout.splitlines()
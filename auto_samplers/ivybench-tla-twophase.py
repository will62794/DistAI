import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def tMRcvPrepared_prec(rm):
	if not (tm_init[0]):
		return False
	if not (msg_prepared[rm]):
		return False
	return True

def tMRcvPrepared(rm):
	tm_prepared[rm] = True

def tMCommit_prec():
	if not (tm_init[0]):
		return False
	if not (forall_func_1(resource_manager_num, (lambda R : tm_prepared[R]))):
		return False
	return True

def tMCommit():
	tm_init[0] = False
	tm_committed[0] = True
	tm_aborted[0] = False
	msg_commit[0] = True

def tMAbort_prec():
	if not (tm_init[0]):
		return False
	return True

def tMAbort():
	tm_init[0] = False
	tm_committed[0] = False
	tm_aborted[0] = True
	msg_abort[0] = True

def rMPrepare_prec(rm):
	if not (working[rm]):
		return False
	return True

def rMPrepare(rm):
	working[rm] = False
	prepared[rm] = True
	committed[rm] = False
	aborted[rm] = False
	msg_prepared[rm] = True

def rMChooseToAbort_prec(rm):
	if not (working[rm]):
		return False
	return True

def rMChooseToAbort(rm):
	working[rm] = False
	prepared[rm] = False
	committed[rm] = False
	aborted[rm] = True

def rMRcvCommitMsg_prec(rm):
	if not (msg_commit[0]):
		return False
	return True

def rMRcvCommitMsg(rm):
	working[rm] = False
	prepared[rm] = False
	committed[rm] = True
	aborted[rm] = False

def rMRcvAbortMsg_prec(rm):
	if not (msg_abort[0]):
		return False
	return True

def rMRcvAbortMsg(rm):
	working[rm] = False
	prepared[rm] = False
	committed[rm] = False
	aborted[rm] = True


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

func_from_name = {'tMRcvPrepared': tMRcvPrepared, 'tMRcvPrepared_prec': tMRcvPrepared_prec, 'tMCommit': tMCommit, 'tMCommit_prec': tMCommit_prec, 'tMAbort': tMAbort, 'tMAbort_prec': tMAbort_prec, 'rMPrepare': rMPrepare, 'rMPrepare_prec': rMPrepare_prec, 'rMChooseToAbort': rMChooseToAbort, 'rMChooseToAbort_prec': rMChooseToAbort_prec, 'rMRcvCommitMsg': rMRcvCommitMsg, 'rMRcvCommitMsg_prec': rMRcvCommitMsg_prec, 'rMRcvAbortMsg': rMRcvAbortMsg, 'rMRcvAbortMsg_prec': rMRcvAbortMsg_prec}

def instance_generator():
	resource_manager_num = rng.integers(1, 5)
	return resource_manager_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global resource_manager_num, working, prepared, committed, aborted, tm_prepared, msg_prepared, tm_init, tm_committed, tm_aborted, msg_commit, msg_abort
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		resource_manager_num = instance_generator()
		working = rng.integers(0, 2, size=(resource_manager_num), dtype=bool)
		prepared = rng.integers(0, 2, size=(resource_manager_num), dtype=bool)
		committed = rng.integers(0, 2, size=(resource_manager_num), dtype=bool)
		aborted = rng.integers(0, 2, size=(resource_manager_num), dtype=bool)
		tm_prepared = rng.integers(0, 2, size=(resource_manager_num), dtype=bool)
		msg_prepared = rng.integers(0, 2, size=(resource_manager_num), dtype=bool)
		tm_init = rng.integers(0, 2, size=(1), dtype=bool)
		tm_committed = rng.integers(0, 2, size=(1), dtype=bool)
		tm_aborted = rng.integers(0, 2, size=(1), dtype=bool)
		msg_commit = rng.integers(0, 2, size=(1), dtype=bool)
		msg_abort = rng.integers(0, 2, size=(1), dtype=bool)
		
		for R in range(resource_manager_num):
			working[R] = True
		for R in range(resource_manager_num):
			prepared[R] = False
		for R in range(resource_manager_num):
			committed[R] = False
		for R in range(resource_manager_num):
			aborted[R] = False
		tm_init[0] = True
		tm_committed[0] = False
		tm_aborted[0] = False
		for R in range(resource_manager_num):
			tm_prepared[R] = False
		for R in range(resource_manager_num):
			msg_prepared[R] = False
		msg_commit[0] = False
		msg_abort[0] = False

		action_pool = ['tMRcvPrepared', 'tMCommit', 'tMAbort', 'rMPrepare', 'rMChooseToAbort', 'rMRcvCommitMsg', 'rMRcvAbortMsg']
		argument_pool = dict()
		argument_pool['tMRcvPrepared'] = []
		for rm in range(resource_manager_num):
			argument_pool['tMRcvPrepared'].append((rm,))
		argument_pool['tMCommit'] = []
		argument_pool['tMCommit'].append(())
		argument_pool['tMAbort'] = []
		argument_pool['tMAbort'].append(())
		argument_pool['rMPrepare'] = []
		for rm in range(resource_manager_num):
			argument_pool['rMPrepare'].append((rm,))
		argument_pool['rMChooseToAbort'] = []
		for rm in range(resource_manager_num):
			argument_pool['rMChooseToAbort'].append((rm,))
		argument_pool['rMRcvCommitMsg'] = []
		for rm in range(resource_manager_num):
			argument_pool['rMRcvCommitMsg'].append((rm,))
		argument_pool['rMRcvAbortMsg'] = []
		for rm in range(resource_manager_num):
			argument_pool['rMRcvAbortMsg'].append((rm,))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				resource_manager_indices = rng.choice(list(range(resource_manager_num)), 1, replace=False)
				resource_manager_indices = sorted(resource_manager_indices)
				for R1, in permutations(resource_manager_indices):
					df_data.add((working[R1], prepared[R1], committed[R1], aborted[R1], tm_prepared[R1], msg_prepared[R1], tm_init[0], tm_committed[0], tm_aborted[0], msg_commit[0], msg_abort[0]))

		collect_subsamples()
		for curr_iter in range(max_iter):
			rng.shuffle(action_pool)
			action_selected, args_selected = None, None
			for action in action_pool:
				rng.shuffle(argument_pool[action])
				argument_candidates = argument_pool[action]
				for args_candidate in argument_candidates:
					if func_from_name[action + '_prec'](*args_candidate):
						action_selected, args_selected = action, args_candidate
						break
				if action_selected is not None:
					break
			if action_selected is None:
				# action pool exhausted, start a new simulation
				break
			func_from_name[action_selected](*args_selected)
			collect_subsamples()

		simulation_round += 1
		df_size_history.append(len(df_data))
		stopping_criteria = simulation_round > 1000 or (simulation_round > 20 and df_size_history[-1] == df_size_history[-21])
	add_checked_candidates()
	return list(df_data)

if __name__ == '__main__':
	start_time = time.time()
	df_data = sample()
	df = pd.DataFrame(df_data, columns=['working(R1)', 'prepared(R1)', 'committed(R1)', 'aborted(R1)', 'tm_prepared(R1)', 'msg_prepared(R1)', 'tm_init', 'tm_committed', 'tm_aborted', 'msg_commit', 'msg_abort'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-tla-twophase.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-tla-twophase.csv')

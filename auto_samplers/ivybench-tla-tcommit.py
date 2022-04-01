import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def prepare_prec(rm):
	if not (working[rm]):
		return False
	return True

def prepare(rm):
	working[rm] = False
	prepared[rm] = True
	committed[rm] = False
	aborted[rm] = False

def decide_commit_prec(rm):
	if not (prepared[rm]):
		return False
	if not (forall_func_1(resource_manager_num, (lambda R : (prepared[R]) or (committed[R])))):
		return False
	return True

def decide_commit(rm):
	working[rm] = False
	prepared[rm] = False
	committed[rm] = True
	aborted[rm] = False

def decide_abort_prec(rm):
	if not ((working[rm]) or (prepared[rm])):
		return False
	if not (forall_func_1(resource_manager_num, (lambda R : not (committed[R])))):
		return False
	return True

def decide_abort(rm):
	working[rm] = False
	prepared[rm] = False
	committed[rm] = False
	aborted[rm] = True


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

func_from_name = {'prepare': prepare, 'prepare_prec': prepare_prec, 'decide_commit': decide_commit, 'decide_commit_prec': decide_commit_prec, 'decide_abort': decide_abort, 'decide_abort_prec': decide_abort_prec}

def instance_generator():
	resource_manager_num = rng.integers(1, 5)
	return resource_manager_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global resource_manager_num, working, prepared, committed, aborted
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
		
		for R in range(resource_manager_num):
			working[R] = True
		for R in range(resource_manager_num):
			prepared[R] = False
		for R in range(resource_manager_num):
			committed[R] = False
		for R in range(resource_manager_num):
			aborted[R] = False

		action_pool = ['prepare', 'decide_commit', 'decide_abort']
		argument_pool = dict()
		argument_pool['prepare'] = []
		for rm in range(resource_manager_num):
			argument_pool['prepare'].append((rm,))
		argument_pool['decide_commit'] = []
		for rm in range(resource_manager_num):
			argument_pool['decide_commit'].append((rm,))
		argument_pool['decide_abort'] = []
		for rm in range(resource_manager_num):
			argument_pool['decide_abort'].append((rm,))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				resource_manager_indices = rng.choice(list(range(resource_manager_num)), 1, replace=False)
				resource_manager_indices = sorted(resource_manager_indices)
				for R1, in permutations(resource_manager_indices):
					df_data.add((working[R1], prepared[R1], committed[R1], aborted[R1]))

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
	df = pd.DataFrame(df_data, columns=['working(R1)', 'prepared(R1)', 'committed(R1)', 'aborted(R1)'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-tla-tcommit.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-tla-tcommit.csv')

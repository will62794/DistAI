import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def choose_prec(v):
	if not (forall_func_1(value_num, (lambda V : not (chosen[V])))):
		return False
	return True

def choose(v):
	chosen[v] = True


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

func_from_name = {'choose': choose, 'choose_prec': choose_prec}

def instance_generator():
	value_num = rng.integers(1, 5)
	return value_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global value_num, chosen
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		value_num = instance_generator()
		chosen = rng.integers(0, 2, size=(value_num), dtype=bool)
		
		for V in range(value_num):
			chosen[V] = False

		action_pool = ['choose']
		argument_pool = dict()
		argument_pool['choose'] = []
		for v in range(value_num):
			argument_pool['choose'].append((v,))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				value_indices = rng.choice(list(range(value_num)), 1, replace=False)
				value_indices = sorted(value_indices)
				for V1, in permutations(value_indices):
					df_data.add((chosen[V1]))

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
	df = pd.DataFrame(df_data, columns=['chosen(V1)'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-tla-consensus.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-tla-consensus.csv')

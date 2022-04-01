import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def send_from_internal_prec(src, dst):
	if not (internal[src]):
		return False
	if not (not (internal[dst])):
		return False
	return True

def send_from_internal(src, dst):
	sent[src, dst] = True
	allowed_in[dst] = True

def send_to_internal_prec(src, dst):
	if not (not (internal[src])):
		return False
	if not (internal[dst]):
		return False
	if not (allowed_in[src]):
		return False
	return True

def send_to_internal(src, dst):
	sent[src, dst] = True


func_from_name = {'send_from_internal': send_from_internal, 'send_from_internal_prec': send_from_internal_prec, 'send_to_internal': send_to_internal, 'send_to_internal_prec': send_to_internal_prec}

def instance_generator():
	node_num = rng.integers(2, 6)
	return node_num

def add_checked_candidates(candidate0, candidate1):
	with open('../configs/ivybench-pyv-firewall.txt', 'a') as config_file:
		if candidate0:
			config_file.write('checked-inv: sent, 2, 0, node, N\n')
		if candidate1:
			config_file.write('checked-inv: sent, 2, 1, node, N\n')

def sample(max_iter=50):
	global node_num, internal, sent, allowed_in
	candidate0, candidate1 = True, True
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		node_num = instance_generator()
		internal = rng.integers(0, 2, size=(node_num), dtype=bool)
		sent = rng.integers(0, 2, size=(node_num, node_num), dtype=bool)
		allowed_in = rng.integers(0, 2, size=(node_num), dtype=bool)
		
		for S in range(node_num):
			for D in range(node_num):
				sent[S, D] = False
		for N in range(node_num):
			allowed_in[N] = False

		action_pool = ['send_from_internal', 'send_to_internal']
		argument_pool = dict()
		argument_pool['send_from_internal'] = []
		for src in range(node_num):
			for dst in range(node_num):
				argument_pool['send_from_internal'].append((src, dst))
		argument_pool['send_to_internal'] = []
		for src in range(node_num):
			for dst in range(node_num):
				argument_pool['send_to_internal'].append((src, dst))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				node_indices = rng.choice(list(range(node_num)), 2, replace=False)
				node_indices = sorted(node_indices)
				for N1, N2, in permutations(node_indices):
					df_data.add((internal[N1], internal[N2], sent[N1,N1], sent[N1,N2], sent[N2,N1], sent[N2,N2], allowed_in[N1], allowed_in[N2]))

		collect_subsamples()
		for curr_iter in range(max_iter):
			# check some candidate invariants
			if rng.random() < .2:
				for N0 in range(node_num):
					for N1 in range(node_num):
						for N2 in range(node_num):
							if candidate0:
								if N0 != N2 and sent[N0, N1] and sent[N2, N1]:
									candidate0 = False
							if candidate1:
								if N1 != N2 and sent[N0, N1] and sent[N0, N2]:
									candidate1 = False
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
	add_checked_candidates(candidate0, candidate1)
	return list(df_data)

if __name__ == '__main__':
	start_time = time.time()
	df_data = sample()
	df = pd.DataFrame(df_data, columns=['internal(N1)', 'internal(N2)', 'sent(N1,N1)', 'sent(N1,N2)', 'sent(N2,N1)', 'sent(N2,N2)', 'allowed_in(N1)', 'allowed_in(N2)'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-pyv-firewall.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-pyv-firewall.csv')

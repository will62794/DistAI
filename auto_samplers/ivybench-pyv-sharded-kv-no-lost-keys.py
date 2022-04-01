import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def reshard_prec(k, v, n_old, n_new):
	if not (table[n_old, k, v]):
		return False
	return True

def reshard(k, v, n_old, n_new):
	table[n_old, k, v] = False
	owner[n_old, k] = False
	transfer_msg[n_new, k, v] = True

def recv_transfer_msg_prec(n, k, v):
	if not (transfer_msg[n, k, v]):
		return False
	return True

def recv_transfer_msg(n, k, v):
	transfer_msg[n, k, v] = False
	table[n, k, v] = True
	owner[n, k] = True

def put_prec(k, v):
	n = owner_f[k]
	return True

def put(k, v):
	n = owner_f[k]
	for V in range(value_num):
		table[n, k, V] = (V) == (v)


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

def exists_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if func(x1):
			return True
	return False

func_from_name = {'reshard': reshard, 'reshard_prec': reshard_prec, 'recv_transfer_msg': recv_transfer_msg, 'recv_transfer_msg_prec': recv_transfer_msg_prec, 'put': put, 'put_prec': put_prec}

def instance_generator():
	key_num = rng.integers(2, 6)
	value_num = rng.integers(3, 7)
	node_num = rng.integers(2, 6)
	return key_num, value_num, node_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global key_num, value_num, node_num, table, owner, transfer_msg, owner_f
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		key_num, value_num, node_num = instance_generator()
		table = rng.integers(0, 2, size=(node_num, key_num, value_num), dtype=bool)
		transfer_msg = rng.integers(0, 2, size=(node_num, key_num, value_num), dtype=bool)
		# the following code block applies rejection sampling to generate predicates that satisfy axiom:
		# (forall K. exists N. owner(N, K))
		# you may consider manually improving its efficiency
		predicates_valid = False
		for retry in range(10):
			owner = np.zeros((node_num, key_num), dtype=bool)
			owner_f = rng.integers(0, node_num, size=(key_num))
			for i in range(key_num):
				owner[owner_f[i], i] = True
			if (forall_func_1(key_num, (lambda K : exists_func_1(node_num, (lambda N : owner[N, K]))))):
				predicates_valid = True
				break
		if not predicates_valid:
			continue
		
		
		for K in range(key_num):
			for V in range(value_num):
				for N in range(node_num):
					table[N, K, V] = False
		for K in range(key_num):
			for V in range(value_num):
				for N in range(node_num):
					transfer_msg[N, K, V] = False

		action_pool = ['reshard', 'recv_transfer_msg', 'put']
		argument_pool = dict()
		argument_pool['reshard'] = []
		for k in range(key_num):
			for v in range(value_num):
				for n_old in range(node_num):
					for n_new in range(node_num):
						argument_pool['reshard'].append((k, v, n_old, n_new))
		argument_pool['recv_transfer_msg'] = []
		for n in range(node_num):
			for k in range(key_num):
				for v in range(value_num):
					argument_pool['recv_transfer_msg'].append((n, k, v))
		argument_pool['put'] = []
		for k in range(key_num):
			for v in range(value_num):
				argument_pool['put'].append((k, v))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				key_indices = rng.choice(list(range(key_num)), 2, replace=False)
				key_indices = sorted(key_indices)
				value_indices = rng.choice(list(range(value_num)), 3, replace=False)
				value_indices = sorted(value_indices)
				node_indices = rng.choice(list(range(node_num)), 2, replace=False)
				node_indices = sorted(node_indices)
				for K1, K2, in permutations(key_indices):
					for V1, V2, V3, in permutations(value_indices):
						for N1, N2, in permutations(node_indices):
							df_data.add((table[N1,K1,V1], table[N1,K1,V2], table[N1,K1,V3], table[N1,K2,V1], table[N1,K2,V2], table[N1,K2,V3], table[N2,K1,V1], table[N2,K1,V2], table[N2,K1,V3], table[N2,K2,V1], table[N2,K2,V2], table[N2,K2,V3], owner[N1,K1], owner[N1,K2], owner[N2,K1], owner[N2,K2], transfer_msg[N1,K1,V1], transfer_msg[N1,K1,V2], transfer_msg[N1,K1,V3], transfer_msg[N1,K2,V1], transfer_msg[N1,K2,V2], transfer_msg[N1,K2,V3], transfer_msg[N2,K1,V1], transfer_msg[N2,K1,V2], transfer_msg[N2,K1,V3], transfer_msg[N2,K2,V1], transfer_msg[N2,K2,V2], transfer_msg[N2,K2,V3]))

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
	df = pd.DataFrame(df_data, columns=['table(N1,K1,V1)', 'table(N1,K1,V2)', 'table(N1,K1,V3)', 'table(N1,K2,V1)', 'table(N1,K2,V2)', 'table(N1,K2,V3)', 'table(N2,K1,V1)', 'table(N2,K1,V2)', 'table(N2,K1,V3)', 'table(N2,K2,V1)', 'table(N2,K2,V2)', 'table(N2,K2,V3)', 'owner(N1,K1)', 'owner(N1,K2)', 'owner(N2,K1)', 'owner(N2,K2)', 'transfer_msg(N1,K1,V1)', 'transfer_msg(N1,K1,V2)', 'transfer_msg(N1,K1,V3)', 'transfer_msg(N1,K2,V1)', 'transfer_msg(N1,K2,V2)', 'transfer_msg(N1,K2,V3)', 'transfer_msg(N2,K1,V1)', 'transfer_msg(N2,K1,V2)', 'transfer_msg(N2,K1,V3)', 'transfer_msg(N2,K2,V1)', 'transfer_msg(N2,K2,V2)', 'transfer_msg(N2,K2,V3)'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-pyv-sharded-kv-no-lost-keys.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-pyv-sharded-kv-no-lost-keys.csv')

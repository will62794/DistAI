import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def new_packet_prec(ps, pd):
	return True

def new_packet(ps, pd):
	pending[ps, pd, ps, ps] = True

def forward_prec(ps, pd, sw0, sw1, nondet):
	if not (pending[ps, pd, sw0, sw1]):
		return False
	return True

def forward(ps, pd, sw0, sw1, nondet):
	for PD in range(node_num):
		for D in range(node_num):
			for PS in range(node_num):
				for S in range(node_num):
					pending[PS, PD, S, D] = (pending[PS, PD, S, D]) and ((PS) == (nondet))
	for D in range(node_num):
		pending[ps, pd, sw1, D] = True
	if ((ps) != (sw1)) and (forall_func_1(node_num, (lambda W : (not ((W) != (sw1))) or (not (table[ps, sw1, W]))))):
		for N1 in range(node_num):
			for N2 in range(node_num):
				table[ps, N1, N2] = (table[ps, N1, N2]) or ((table[ps, N1, sw1]) and (table[ps, sw0, N2]))


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

func_from_name = {'new_packet': new_packet, 'new_packet_prec': new_packet_prec, 'forward': forward, 'forward_prec': forward_prec}

def instance_generator():
	node_num = rng.integers(4, 8)
	return node_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global node_num, table, pending
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		node_num = instance_generator()
		table = rng.integers(0, 2, size=(node_num, node_num, node_num), dtype=bool)
		pending = rng.integers(0, 2, size=(node_num, node_num, node_num, node_num), dtype=bool)
		
		for N1 in range(node_num):
			for N2 in range(node_num):
				for T in range(node_num):
					table[T, N1, N2] = (N1) == (N2)
		for PD in range(node_num):
			for D in range(node_num):
				for PS in range(node_num):
					for S in range(node_num):
						pending[PS, PD, S, D] = False

		action_pool = ['new_packet', 'forward']
		argument_pool = dict()
		argument_pool['new_packet'] = []
		for ps in range(node_num):
			for pd in range(node_num):
				argument_pool['new_packet'].append((ps, pd))
		argument_pool['forward'] = []
		for ps in range(node_num):
			for pd in range(node_num):
				for sw0 in range(node_num):
					for sw1 in range(node_num):
						for nondet in range(node_num):
							argument_pool['forward'].append((ps, pd, sw0, sw1, nondet))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				node_indices = rng.choice(list(range(node_num)), 4, replace=False)
				node_indices = sorted(node_indices)
				for N1, N2, N3, N4, in permutations(node_indices):
					df_data.add((table[N1,N1,N1], table[N1,N1,N2], table[N1,N1,N3], table[N1,N1,N4], table[N1,N2,N1], table[N1,N2,N2], table[N1,N2,N3], table[N1,N2,N4], table[N1,N3,N1], table[N1,N3,N2], table[N1,N3,N3], table[N1,N3,N4], table[N1,N4,N1], table[N1,N4,N2], table[N1,N4,N3], table[N1,N4,N4], table[N2,N1,N1], table[N2,N1,N2], table[N2,N1,N3], table[N2,N1,N4], table[N2,N2,N1], table[N2,N2,N2], table[N2,N2,N3], table[N2,N2,N4], table[N2,N3,N1], table[N2,N3,N2], table[N2,N3,N3], table[N2,N3,N4], table[N2,N4,N1], table[N2,N4,N2], table[N2,N4,N3], table[N2,N4,N4], table[N3,N1,N1], table[N3,N1,N2], table[N3,N1,N3], table[N3,N1,N4], table[N3,N2,N1], table[N3,N2,N2], table[N3,N2,N3], table[N3,N2,N4], table[N3,N3,N1], table[N3,N3,N2], table[N3,N3,N3], table[N3,N3,N4], table[N3,N4,N1], table[N3,N4,N2], table[N3,N4,N3], table[N3,N4,N4], table[N4,N1,N1], table[N4,N1,N2], table[N4,N1,N3], table[N4,N1,N4], table[N4,N2,N1], table[N4,N2,N2], table[N4,N2,N3], table[N4,N2,N4], table[N4,N3,N1], table[N4,N3,N2], table[N4,N3,N3], table[N4,N3,N4], table[N4,N4,N1], table[N4,N4,N2], table[N4,N4,N3], table[N4,N4,N4], pending[N1,N1,N1,N1], pending[N1,N1,N1,N2], pending[N1,N1,N1,N3], pending[N1,N1,N1,N4], pending[N1,N1,N2,N1], pending[N1,N1,N2,N2], pending[N1,N1,N2,N3], pending[N1,N1,N2,N4], pending[N1,N1,N3,N1], pending[N1,N1,N3,N2], pending[N1,N1,N3,N3], pending[N1,N1,N3,N4], pending[N1,N1,N4,N1], pending[N1,N1,N4,N2], pending[N1,N1,N4,N3], pending[N1,N1,N4,N4], pending[N1,N2,N1,N1], pending[N1,N2,N1,N2], pending[N1,N2,N1,N3], pending[N1,N2,N1,N4], pending[N1,N2,N2,N1], pending[N1,N2,N2,N2], pending[N1,N2,N2,N3], pending[N1,N2,N2,N4], pending[N1,N2,N3,N1], pending[N1,N2,N3,N2], pending[N1,N2,N3,N3], pending[N1,N2,N3,N4], pending[N1,N2,N4,N1], pending[N1,N2,N4,N2], pending[N1,N2,N4,N3], pending[N1,N2,N4,N4]))

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
	df = pd.DataFrame(df_data, columns=['table(N1,N1,N1)', 'table(N1,N1,N2)', 'table(N1,N1,N3)', 'table(N1,N1,N4)', 'table(N1,N2,N1)', 'table(N1,N2,N2)', 'table(N1,N2,N3)', 'table(N1,N2,N4)', 'table(N1,N3,N1)', 'table(N1,N3,N2)', 'table(N1,N3,N3)', 'table(N1,N3,N4)', 'table(N1,N4,N1)', 'table(N1,N4,N2)', 'table(N1,N4,N3)', 'table(N1,N4,N4)', 'table(N2,N1,N1)', 'table(N2,N1,N2)', 'table(N2,N1,N3)', 'table(N2,N1,N4)', 'table(N2,N2,N1)', 'table(N2,N2,N2)', 'table(N2,N2,N3)', 'table(N2,N2,N4)', 'table(N2,N3,N1)', 'table(N2,N3,N2)', 'table(N2,N3,N3)', 'table(N2,N3,N4)', 'table(N2,N4,N1)', 'table(N2,N4,N2)', 'table(N2,N4,N3)', 'table(N2,N4,N4)', 'table(N3,N1,N1)', 'table(N3,N1,N2)', 'table(N3,N1,N3)', 'table(N3,N1,N4)', 'table(N3,N2,N1)', 'table(N3,N2,N2)', 'table(N3,N2,N3)', 'table(N3,N2,N4)', 'table(N3,N3,N1)', 'table(N3,N3,N2)', 'table(N3,N3,N3)', 'table(N3,N3,N4)', 'table(N3,N4,N1)', 'table(N3,N4,N2)', 'table(N3,N4,N3)', 'table(N3,N4,N4)', 'table(N4,N1,N1)', 'table(N4,N1,N2)', 'table(N4,N1,N3)', 'table(N4,N1,N4)', 'table(N4,N2,N1)', 'table(N4,N2,N2)', 'table(N4,N2,N3)', 'table(N4,N2,N4)', 'table(N4,N3,N1)', 'table(N4,N3,N2)', 'table(N4,N3,N3)', 'table(N4,N3,N4)', 'table(N4,N4,N1)', 'table(N4,N4,N2)', 'table(N4,N4,N3)', 'table(N4,N4,N4)', 'pending(N1,N1,N1,N1)', 'pending(N1,N1,N1,N2)', 'pending(N1,N1,N1,N3)', 'pending(N1,N1,N1,N4)', 'pending(N1,N1,N2,N1)', 'pending(N1,N1,N2,N2)', 'pending(N1,N1,N2,N3)', 'pending(N1,N1,N2,N4)', 'pending(N1,N1,N3,N1)', 'pending(N1,N1,N3,N2)', 'pending(N1,N1,N3,N3)', 'pending(N1,N1,N3,N4)', 'pending(N1,N1,N4,N1)', 'pending(N1,N1,N4,N2)', 'pending(N1,N1,N4,N3)', 'pending(N1,N1,N4,N4)', 'pending(N1,N2,N1,N1)', 'pending(N1,N2,N1,N2)', 'pending(N1,N2,N1,N3)', 'pending(N1,N2,N1,N4)', 'pending(N1,N2,N2,N1)', 'pending(N1,N2,N2,N2)', 'pending(N1,N2,N2,N3)', 'pending(N1,N2,N2,N4)', 'pending(N1,N2,N3,N1)', 'pending(N1,N2,N3,N2)', 'pending(N1,N2,N3,N3)', 'pending(N1,N2,N3,N4)', 'pending(N1,N2,N4,N1)', 'pending(N1,N2,N4,N2)', 'pending(N1,N2,N4,N3)', 'pending(N1,N2,N4,N4)'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-pyv-learning-switch.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-pyv-learning-switch.csv')

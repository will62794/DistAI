import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def vote_prec(v, n):
	if not (forall_func_1(node_num, (lambda M : not (voted[v, M])))):
		return False
	return True

def vote(v, n):
	voted[v, n] = True

def become_leader_prec(n, s):
	if not (majority[s]):
		return False
	if not (forall_func_1(node_num, (lambda M : (not (member[M, s])) or (voted[M, n])))):
		return False
	return True

def become_leader(n, s):
	isleader[n] = True
	quorum[0] = s


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

def forall_func_3(domain_size_1, domain_size_2, domain_size_3, func):
	for x1 in range(domain_size_1):
		for x2 in range(domain_size_2):
			for x3 in range(domain_size_3):
				if not func(x1, x2, x3):
					return False
	return True

def exists_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if func(x1):
			return True
	return False

func_from_name = {'vote': vote, 'vote_prec': vote_prec, 'become_leader': become_leader, 'become_leader_prec': become_leader_prec}

def instance_generator():
	node_num = rng.integers(2, 6)
	nset_num = rng.integers(1, 5)
	return node_num, nset_num

def add_checked_candidates(candidate0, candidate1):
	with open('../configs/ex-quorum-leader-election.txt', 'a') as config_file:
		if candidate0:
			config_file.write('checked-inv: voted, 2, 0, node, NO\n')
		if candidate1:
			config_file.write('checked-inv: voted, 2, 1, node, NO\n')

def sample(max_iter=50):
	global node_num, nset_num, isleader, voted, member, majority, quorum
	candidate0, candidate1 = True, True
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		node_num, nset_num = instance_generator()
		isleader = rng.integers(0, 2, size=(node_num), dtype=bool)
		voted = rng.integers(0, 2, size=(node_num, node_num), dtype=bool)
		member = rng.integers(0, 2, size=(node_num, nset_num), dtype=bool)
		majority = rng.integers(0, 2, size=(nset_num), dtype=bool)
		quorum = rng.integers(0, nset_num, size=(1))
		# the following code block applies rejection sampling to generate predicates that satisfy axiom:
		# majority(S) & majority(Y) -> exists N . member(N, S) & member(N, T)
		# you may consider manually improving its efficiency
		predicates_valid = False
		for retry in range(10):
			majority = rng.integers(0, 2, size=(nset_num), dtype=bool)
			member = rng.integers(0, 2, size=(node_num, nset_num), dtype=bool)
			if (forall_func_3(nset_num, nset_num, nset_num, (lambda S,T,Y : (not ((majority[S]) and (majority[Y]))) or (exists_func_1(node_num, (lambda N : (member[N, S]) and (member[N, T]))))))):
				predicates_valid = True
				break
		if not predicates_valid:
			continue
		
		
		for M in range(node_num):
			for N in range(node_num):
				voted[N, M] = False
		for N in range(node_num):
			isleader[N] = False

		action_pool = ['vote', 'become_leader']
		argument_pool = dict()
		argument_pool['vote'] = []
		for v in range(node_num):
			for n in range(node_num):
				argument_pool['vote'].append((v, n))
		argument_pool['become_leader'] = []
		for n in range(node_num):
			for s in range(nset_num):
				argument_pool['become_leader'].append((n, s))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				node_indices = rng.choice(list(range(node_num)), 2, replace=False)
				node_indices = sorted(node_indices)
				nset_indices = rng.choice(list(range(nset_num)), 1, replace=False)
				nset_indices = sorted(nset_indices)
				for NO1, NO2, in permutations(node_indices):
					for NS1, in permutations(nset_indices):
						df_data.add((isleader[NO1], isleader[NO2], voted[NO1,NO1], voted[NO1,NO2], voted[NO2,NO1], voted[NO2,NO2], member[NO1,NS1], member[NO2,NS1], majority[NS1], quorum[0]==NS1))

		collect_subsamples()
		for curr_iter in range(max_iter):
			# check some candidate invariants
			if rng.random() < .2:
				for NO0 in range(node_num):
					for NO1 in range(node_num):
						for NO2 in range(node_num):
							if candidate0:
								if NO0 != NO2 and voted[NO0, NO1] and voted[NO2, NO1]:
									candidate0 = False
							if candidate1:
								if NO1 != NO2 and voted[NO0, NO1] and voted[NO0, NO2]:
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
	df = pd.DataFrame(df_data, columns=['isleader(NO1)', 'isleader(NO2)', 'voted(NO1,NO1)', 'voted(NO1,NO2)', 'voted(NO2,NO1)', 'voted(NO2,NO2)', 'member(NO1,NS1)', 'member(NO2,NS1)', 'majority(NS1)', 'quorum=NS1'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ex-quorum-leader-election.csv', index=False)
	print('Simulation finished. Trace written to traces/ex-quorum-leader-election.csv')

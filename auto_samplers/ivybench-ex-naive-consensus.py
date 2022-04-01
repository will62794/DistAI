import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def cast_vote_prec(n, v):
	if not (forall_func_1(value_num, (lambda V : not (vote[n, V])))):
		return False
	return True

def cast_vote(n, v):
	vote[n, v] = True

def collect_votes_prec(q, v):
	if not (forall_func_1(node_num, (lambda N : (not (member[N, q])) or (vote[N, v])))):
		return False
	return True

def collect_votes(q, v):
	decide[q, v] = True

def learn_value_prec(q, v):
	if not (decide[q, v]):
		return False
	return True

def learn_value(q, v):
	decision[v] = True


def forall_func_1(domain_size_1, func):
	for x1 in range(domain_size_1):
		if not func(x1):
			return False
	return True

func_from_name = {'cast_vote': cast_vote, 'cast_vote_prec': cast_vote_prec, 'collect_votes': collect_votes, 'collect_votes_prec': collect_votes_prec, 'learn_value': learn_value, 'learn_value_prec': learn_value_prec}

def instance_generator():
	node_num = rng.integers(2, 6)
	quorum_num = rng.integers(2, 6)
	value_num = rng.integers(2, 6)
	return node_num, quorum_num, value_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global node_num, quorum_num, value_num, member, vote, decide, decision
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		node_num, quorum_num, value_num = instance_generator()
		member = rng.integers(0, 2, size=(node_num, quorum_num), dtype=bool)
		vote = rng.integers(0, 2, size=(node_num, value_num), dtype=bool)
		decide = rng.integers(0, 2, size=(quorum_num, value_num), dtype=bool)
		decision = rng.integers(0, 2, size=(value_num), dtype=bool)
		member = np.zeros((node_num, quorum_num), dtype=bool)
		for q in range(quorum_num):
			qsize = rng.integers(1, node_num + 1)
			qsize_succeed = False
			# choose a random size for this quorum, increment if infeasible, when size == node_num it must be feasible
			while not qsize_succeed:
				node_combs_this_qsize = list(combinations(list(range(node_num)), qsize))
				rng.shuffle(node_combs_this_qsize)
				for node_comb in node_combs_this_qsize:
					# check if this quorum is compatible (i.e., shares one element in common) with previous quorums
					is_valid_node_comb = True
					for existing_q in range(0, q):
						this_existing_q_has_common_element = False
						for node in node_comb:
							if member[node, existing_q]:
								this_existing_q_has_common_element = True
								break
						if not this_existing_q_has_common_element:
							is_valid_node_comb = False
							break
					if is_valid_node_comb:
						qsize_succeed = True
						for node in node_comb:
							member[node, q] = True
						break
				qsize += 1
		rng.shuffle(member, axis=1)
		
		for N in range(node_num):
			for V in range(value_num):
				vote[N, V] = False
		for V in range(value_num):
			for Q in range(quorum_num):
				decide[Q, V] = False
		for V in range(value_num):
			decision[V] = False

		action_pool = ['cast_vote', 'collect_votes', 'learn_value']
		argument_pool = dict()
		argument_pool['cast_vote'] = []
		for n in range(node_num):
			for v in range(value_num):
				argument_pool['cast_vote'].append((n, v))
		argument_pool['collect_votes'] = []
		for q in range(quorum_num):
			for v in range(value_num):
				argument_pool['collect_votes'].append((q, v))
		argument_pool['learn_value'] = []
		for q in range(quorum_num):
			for v in range(value_num):
				argument_pool['learn_value'].append((q, v))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				node_indices = rng.choice(list(range(node_num)), 2, replace=False)
				node_indices = sorted(node_indices)
				quorum_indices = rng.choice(list(range(quorum_num)), 2, replace=False)
				quorum_indices = sorted(quorum_indices)
				value_indices = rng.choice(list(range(value_num)), 2, replace=False)
				value_indices = sorted(value_indices)
				for N1, N2, in permutations(node_indices):
					for Q1, Q2, in permutations(quorum_indices):
						for V1, V2, in permutations(value_indices):
							df_data.add((member[N1,Q1], member[N1,Q2], member[N2,Q1], member[N2,Q2], vote[N1,V1], vote[N1,V2], vote[N2,V1], vote[N2,V2], decide[Q1,V1], decide[Q1,V2], decide[Q2,V1], decide[Q2,V2], decision[V1], decision[V2]))

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
	df = pd.DataFrame(df_data, columns=['member(N1,Q1)', 'member(N1,Q2)', 'member(N2,Q1)', 'member(N2,Q2)', 'vote(N1,V1)', 'vote(N1,V2)', 'vote(N2,V1)', 'vote(N2,V2)', 'decide(Q1,V1)', 'decide(Q1,V2)', 'decide(Q2,V1)', 'decide(Q2,V2)', 'decision(V1)', 'decision(V2)'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-ex-naive-consensus.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-ex-naive-consensus.csv')

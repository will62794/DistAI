import numpy as np
from collections import defaultdict
from scipy.special import comb
import time
import pandas as pd
from itertools import product, permutations, combinations

rng = np.random.default_rng(0)
bool_num = 2

def lock_prec(n):
	return True

def lock(n):
	lock_msg[n] = True

def unlock_prec(n):
	if not (holds_lock[n]):
		return False
	return True

def unlock(n):
	holds_lock[n] = False
	unlock_msg[n] = True

def recv_lock_prec(sender):
	if not (lock_msg[sender]):
		return False
	if not (not (held[0])):
		return False
	return True

def recv_lock(sender):
	held[0] = True
	lock_msg[sender] = False
	grant_msg[sender] = True

def recv_grant_prec(n):
	if not (grant_msg[n]):
		return False
	return True

def recv_grant(n):
	grant_msg[n] = False
	holds_lock[n] = True

def recv_unlock_prec(sender):
	if not (unlock_msg[sender]):
		return False
	return True

def recv_unlock(sender):
	unlock_msg[sender] = False
	held[0] = False


func_from_name = {'lock': lock, 'lock_prec': lock_prec, 'unlock': unlock, 'unlock_prec': unlock_prec, 'recv_lock': recv_lock, 'recv_lock_prec': recv_lock_prec, 'recv_grant': recv_grant, 'recv_grant_prec': recv_grant_prec, 'recv_unlock': recv_unlock, 'recv_unlock_prec': recv_unlock_prec}

def instance_generator():
	node_num = rng.integers(2, 6)
	return node_num

def add_checked_candidates():
	return

def sample(max_iter=50):
	global node_num, lock_msg, unlock_msg, grant_msg, holds_lock, held
	df_data = set()
	stopping_criteria = False
	simulation_round = 0
	df_size_history = [0]
	while stopping_criteria is False:
		# protocol initialization
		node_num = instance_generator()
		lock_msg = rng.integers(0, 2, size=(node_num), dtype=bool)
		unlock_msg = rng.integers(0, 2, size=(node_num), dtype=bool)
		grant_msg = rng.integers(0, 2, size=(node_num), dtype=bool)
		holds_lock = rng.integers(0, 2, size=(node_num), dtype=bool)
		held = rng.integers(0, 2, size=(1), dtype=bool)
		
		for N in range(node_num):
			lock_msg[N] = False
		for N in range(node_num):
			unlock_msg[N] = False
		for N in range(node_num):
			grant_msg[N] = False
		for N in range(node_num):
			holds_lock[N] = False
		held[0] = False

		action_pool = ['lock', 'unlock', 'recv_lock', 'recv_grant', 'recv_unlock']
		argument_pool = dict()
		argument_pool['lock'] = []
		for n in range(node_num):
			argument_pool['lock'].append((n,))
		argument_pool['unlock'] = []
		for n in range(node_num):
			argument_pool['unlock'].append((n,))
		argument_pool['recv_lock'] = []
		for sender in range(node_num):
			argument_pool['recv_lock'].append((sender,))
		argument_pool['recv_grant'] = []
		for n in range(node_num):
			argument_pool['recv_grant'].append((n,))
		argument_pool['recv_unlock'] = []
		for sender in range(node_num):
			argument_pool['recv_unlock'].append((sender,))

		def collect_subsamples():
			# generate subsamples from the current state (sample)
			for k in range(3):
				node_indices = rng.choice(list(range(node_num)), 2, replace=False)
				node_indices = sorted(node_indices)
				for N1, N2, in permutations(node_indices):
					df_data.add((lock_msg[N1], lock_msg[N2], unlock_msg[N1], unlock_msg[N2], grant_msg[N1], grant_msg[N2], holds_lock[N1], holds_lock[N2], held[0]))

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
	df = pd.DataFrame(df_data, columns=['lock_msg(N1)', 'lock_msg(N2)', 'unlock_msg(N1)', 'unlock_msg(N2)', 'grant_msg(N1)', 'grant_msg(N2)', 'holds_lock(N1)', 'holds_lock(N2)', 'held'])
	df = df.drop_duplicates().astype(int)
	end_time = time.time()
	df.to_csv('../traces/ivybench-ex-lockserv-automaton.csv', index=False)
	print('Simulation finished. Trace written to traces/ivybench-ex-lockserv-automaton.csv')

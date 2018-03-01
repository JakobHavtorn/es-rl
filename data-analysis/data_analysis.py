import numpy as np
import os


def print_group_info(algorithm_states, groups, directory):
    omit_keys = ['sensitivities', 'sens_inputs', 'chkpt_dir', 'chkpt_int', 'cuda', 'exclude_from_state_dict']
    omit_keys.extend([k for k in algorithm_states[0].keys() if k[0] == '_'])
    _, indices = np.unique(groups, return_index=True)
    unique_states = [algorithm_states[i] for i in indices]
    longest_key_len = 0
    longest_val_len = 0
    for s in unique_states:
        for k, v in s.items():
            if not k in omit_keys:
                longest_key_len = max(longest_key_len, len(k))
                longest_val_len = max(longest_val_len, len(str(v)))
    format_str = '{0:' + str(longest_key_len) + 's}\t{1:' + str(longest_val_len) + 's}\n'
    with open(os.path.join(directory, 'groups.info'), 'w') as f:
        for g_id, s in enumerate(unique_states):
            f.write('='*(len(format_str.format('0', '0'))-1) + '\n')
            f.write(format_str.format('GROUP', str(g_id)))
            for k, v in s.items():
                if not k in omit_keys:
                    f.write(format_str.format(k, str(v)))


def get_best(algorithm_states, key='return_unp', operation='max'):
    """Return the best run among several as measured by `key` and
    the `operation`
    """
    best_id = 0
    best_return = 0
    for i, s in enumerate(algorithm_states):
        if max(s['stats'][key]) > best_return:
            best_return = max(s['stats'][key])
            best_id = i
    return algorithm_states[best_id]


def get_max_chkpt_int(algorithm_states):
    """Get the maximum time in seconds between checkpoints.
    """
    max_chkpt_int = -1
    for s in algorithm_states:
        max_chkpt_int = max(s['chkpt_int'], max_chkpt_int)
    return max_chkpt_int


def invert_signs(stats_list, keys='all'):
    """Invert sign on negative returns.
    
    Negative returns indicate a converted minimization problem so this converts the problem 
    considered to maximization which is the standard in the algorithms.

    Args:
        stats_list (list): [description]
        keys (dict): [description]
    """
    if keys == 'all':
        keys = {'return_unp', 'return_max', 'return_min', 'return_avg'}
    for s in stats_list:
        if (np.array(s['return_unp']) < 0).all():
            for k in {'return_unp', 'return_max', 'return_min', 'return_avg'}.intersection(keys):
                s[k] = [-retrn for retrn in s[k]]


def get_checkpoint_directories(dir):
    return [os.path.join(dir, di) for di in os.listdir(dir) if os.path.isdir(os.path.join(dir, di)) and di != 'monitoring']
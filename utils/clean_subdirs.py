"""Script that removes all files that equal given filenames in all sub directories of a directory.
"""

import os
import argparse
import IPython
import filesystem as fs

if __name__ == '__main__':
    # Ask to continue
    r = input('This script should not be run while algorithms are executing as this risks deleting their checkpoints.\nProceed? (y/n) ')
    if r not in ['y', 'Y']:
        print('Script ended. No files deleted.')
        exit(0)
    
    # Input
    parser = argparse.ArgumentParser(description='Experiments')
    parser.add_argument('-d', type=str, metavar='directory', help='Directory to clean')
    parser.add_argument('-f', type=str, nargs='+', metavar='files', help='File(s) to remove')
    args = parser.parse_args()

    # Validate
    if args.d is None:
        this_file_dir_local = os.path.dirname(os.path.abspath(__file__))
        package_root_this_file = fs.get_parent(this_file_dir_local, 'es-rl')
        args.d = os.path.join(package_root_this_file, 'experiments', 'checkpoints')
    if args.f is None:
        args.keep = ['state-dict-algorithm.pkl', 'stats.csv']
        args.delete = []
        # args.delete = args.f
        # args.f = ['state-dict-best-algorithm.pkl', 'state-dict-best-optimizer.pkl', 
        #           'state-dict-best-model.pkl', 'state-dict-optimizer.pkl',
        #           'state-dict-model.pkl']
    assert args.d is not None and args.delete is not None

    # Run
    for root, directories, filenames in os.walk(args.d):
        i = 0
        for filename in filenames:
            if filename in args.delete:
                os.remove(os.path.join(root, filename))
                i += 1
            if filename not in args.keep:
                os.remove(os.path.join(root, filename))
        if len(filenames) == 1 and filenames[0] == 'init.log':
            os.remove(os.path.join(root, filenames[0]))
            os.rmdir(os.path.join(root))
            i += 1
        if i > 0:
            print('Removed {:d} {:s} in {:s}'.format(i, 'file' if i == 1 else 'files', root))

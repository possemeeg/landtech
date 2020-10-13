' Entry point '
import argparse
import sys
import os
from contextlib import ExitStack

from landtreecli import mk_tree, expand_tree

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('company_id', metavar='company id')
    parser.add_argument('--mode', choices=['from_root', 'expand'],
            required=True)

    args = parser.parse_args()

    with ExitStack() as cleanup_stack:
        relations = cleanup_stack.enter_context(
                open(os.path.join('data', 'company_relations.csv')))
        ownersipes = cleanup_stack.enter_context(
                open(os.path.join('data', 'land_ownership.csv')))

        if args.mode == 'from_root':
            mk_tree(args.company_id, relations, ownersipes, sys.stdout)
        elif args.mode == 'expand':
            expand_tree(args.company_id, relations, ownersipes, sys.stdout)

import sys
import argparse
import logging

from pylib import torrentapi

INDEX_PROVIDERS = ('tpb_api', 'rarbg')

parser = argparse.ArgumentParser()
parser.add_argument(
    "query", help="query a title to retrieve download items", type=str)
parser.add_argument(
    "index", help="the torrent index provider to search", type=str,
    choices=INDEX_PROVIDERS)
args = parser.parse_args()


def run_query():
    if args.index == 'tpb':
        query_method = torrentapi.searchPirateBay
    elif args.index == 'tpb_api':
        query_method = torrentapi.searchPirateBayWithAPI
    elif args.index == 'rarbg':
        query_method = torrentapi.search_rarbg

    search_results = query_method(args.query)
    for sr in search_results:
        print(sr)


if __name__ == '__main__':
    if args.index not in INDEX_PROVIDERS:
        print('%s is not a valid torrent indexer' % args.index)
        sys.exit(1)
    run_query()
#!/home/paulcooper/Documents/dev/autotain/venv/bin/python
import os
import pickle
import sys
import argparse
import logging
from collections import deque, namedtuple
from os.path import join

from torrench.Torrench import Torrench
from torrench.modules import thepiratebay as tpb
from torrench.modules import rarbg

INDEX_PROVIDERS = ('tpb', 'rarbg')

parser = argparse.ArgumentParser()
parser.add_argument(
    "query", help="query a title to retrieve download items", type=str)
parser.add_argument(
    "index", help="the torrent index provider to search", type=str,
    choices=INDEX_PROVIDERS)
args = parser.parse_args()

log = logging.Logger(__name__, level=logging.DEBUG)

Torrent = namedtuple(
    'Torrent', ['title', 'index', 'size', 'ratio', 'uploaded', 'magnet'])


def run_query():
    if args.index == 'tpb':
        client = tpb
    elif args.index == 'rarbg':
        client = rarbg
    return client.cross_site(args.query, 1)


def determine_best_result(results):
    # ensure the actual name of 
    return results[0]


if __name__ == '__main__':
    if args.index not in INDEX_PROVIDERS:
        log.error('%s is not a valid torrent indexer' % args.index)
        sys.exit(1)

    tr = Torrench()
    tr.input_title = args.query
    tr.page_limit = 1

    result = run_query()
    result.proxy = 'https://thepiratebay.org'
    result.get_html()
    result.parse_html()

    torrents = []
    for index, record in enumerate(result.masterlist_crossite):
        magnet = result.mapper[index][1]
        record.append(magnet)
        t = Torrent(*record)
        log.debug("{} size: {} ratio: {}".format(t.title, t.size, t.ratio))
        log.debug(t.magnet)

        torrents.append(t)

    best_choice = determine_best_result(torrents)
    print()
    print(best_choice.magnet)
    print()

    # add magnet link to queue
    queue_file = join(os.path.dirname(__file__), 'queues/magnets.pq')
    try:
        fopen = open(queue_file, 'rb')
        download_queue = pickle.load(fopen, encoding='UTF-8')
    except EOFError:
        # empty file, no queue
        download_queue = deque()

    download_queue.append(best_choice.magnet)
    fopen = open(queue_file, 'wb')
    pickle.dump(download_queue, fopen)

    print('Magnet link added to queue.')

    sys.exit()

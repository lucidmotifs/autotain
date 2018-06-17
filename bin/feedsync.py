""" showrss feed parser task. invoked when a feed has new items. builds 'show'
    objects with a magnet links attached. these objects are pickled and added to
    a file queue. new queue items message is returned to autotain daemon informing
    it that transfer task should be invoked. """
import argparse
import logging
import feedparser

parser = argparse.ArgumentParser()
parser.add_argument(
    "feed", help="create new download_candidates from rss feed", type=str)
args = parser.parse_args()

def run():
    feed = feedparser.parse(args.feed)
    for e in feed.entries:
        print(e['title'])
        print(e['link'])
        print('\n')


if __name__ == '__main__':
    run()
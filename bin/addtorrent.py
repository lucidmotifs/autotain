#!/home/paulcooper/Documents/dev/autotain/venv/bin/python
import os
import pickle
import sys
import time
from enum import Enum
from os import listdir, remove
from os.path import isfile, join

import transmissionrpc

# interface settings
MAX_LINE_LENGTH = 80
UPDATE_TICK_RATE = 5


# typedefs and enums
class TorrentStatus(Enum):
    DOWNLOADING = 'downloading'
    SEEDING = 'seeding'
    PAUSED = 'paused'
    STOPPED = 'stopped'


client = transmissionrpc.Client('localhost', port=9091)

# load deque from magnets file
queue_file = join(os.path.dirname(__file__), 'queues/magnets.pq')
fopen = open(queue_file, 'rb')
download_queue = pickle.load(fopen, encoding='UTF-8')

# add everything in the queue
while(len(download_queue)):
    client.add_torrent(download_queue.popleft())
    # TODO find better method than sleeping
    time.sleep(2)

# save queue
fopen = open(queue_file, 'wb')
pickle.dump(download_queue, fopen)

# would now have to set up multiple listeners to track the downloads
# the below would be run in seperate threads

# get details of last added torrent
torrent_list = client.get_torrents()
torrent = client.get_torrents()[-1]

print("Starting download of {} ({})".format(
    torrent.name, torrent.hashString))
print("Status: {}".format(torrent.status))


def progress_bar(value, endvalue, dl_rate, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    out = "\rProgress: [{0}] {1}% @ {2}kBps".format(
        arrow + spaces, int(round(percent * 100)),
        float(round(dl_rate / 1024, 2)))
    # add padding to keep lines consistent
    out + (' ' * MAX_LINE_LENGTH - len(out))

    sys.stdout.write(out)
    sys.stdout.flush()


try:
    while(torrent.status == TorrentStatus.DOWNLOADING.value):
        progress_bar(torrent.percentDone, 1, torrent.rateDownload, 40)
        time.sleep(UPDATE_TICK_RATE)
        torrent = client.get_torrent(torrent.id)
    print('Finished!')
except Exception:
    print('Exception caught, removing torrent and data')
    client.remove_torrent(id, delete_data=True)
    raise

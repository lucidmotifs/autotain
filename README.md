# autotain
Automation of home entertainment

## Key Features

- Automation of media library creation and management
- Recommendation engine based on aspects of your library
- Multi-user experience
- Discovery engine
- Moment tagging
- Extra content promotion
- Social experiences attached to media consumption
- Feed and schedule planning
- Remote library management (message


## Tech Stack Plans
Rust daemon / message passer calling python scripts that coomunicate with various APIS.
Events, or signals are processed by calling independent modules to perform some task. Python
modules don't talk to each other, they have distinct goals or tasks, and simply report their
progress and results, if approppriate.

## Python Modules
- RSS Feed Parser
- Torrent RPC
- File Managment (Including renaming, etc)
- Meta Data collection / attachment

## Initial Offering
autotain daemon receives message about media item that user wishes to watch.
python module for media data is launched, notifies daemon is disambiguation is required.
new media item and meta data is added to library - daemon is notified new media now exists.
daemon launches python module for media downloading, if series - a new feed it registered with daemon.
python download module works through the queue of requests, each time an item is downloaded the daemon is notified
when daemon receives notification that a new file is ready, it launches file management module.
file management module pushes completed items to gcloud - notifies daemon when transfer is complete
daemon then notifies user that movie is ready / new episode downloaded - etc.

## MVP for Rust Daemon
- Can receive structured messages, and subscribe to events (signal / slot behaviour)
- Run python scripts (jobs?) with the correct arguments.
- Have some way of monitoring the status of requested tasks.
- User notifications.

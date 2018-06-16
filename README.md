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


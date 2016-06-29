## Performance issues

### `ays_bot` workers
The workers process work over gevent queues. First thing the worker do is get the action scope to run by calling `repo.getRun`.
After a bit of testing, I found out that `repo.getRun` is extremely slow even for small installations.

I tried to timeout the call on the gig.bracelona setup and got the following results.

```python
%timeit x = repo.getRun(action='recurring_process_issues_from_github')
#OUT: 1 loop, best of 3: 2min 5s per loop
```

Recalling the method with the same arguments doesn't go faster.

### `ays_bot` events dispatching
When an event is received. The event is dispatched to ALL services that are interested in that event type (generic, email, alarm, etc...).
The dispatching system doesn't care if the event payload is actually intended to this specific service. It's up to the service
to decide if it should process this event or not. Which wasts a LOT of cpu cycles. (Imaging loading the event payload +1000 times
for each service that is trying to process it).

For example, the `github_issue` event is intersted in events of type `genric`. The `generic` channel is the channel that `web hooks`
events come over. This basically mean if ANY generic event is raised all the `github_issue`s handlers will get called for that event.

### jumpscale `action`
All service methods are decorated as `actions`. The legend says we need it this way so it can be tracked (the state of last exection)
and also in case we execute it remotely. This adds a LOT of over head to the simplest action call.

Since each action (on each call) is written to it's own file (the code is even modified and some dependencies are injected) and
then is reloaded as a python module using `importlib` and then executed. Not mentioning the code quality.

A heavy IO operations are involved for each action call, plus string manipulation.

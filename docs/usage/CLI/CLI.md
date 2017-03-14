## Using the AYS CLI


```
ays --help

Usage: ays [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  blueprint    will process the blueprint(s) pointed to it...
  commit       commit the changes in the ays repo to git,...
  create_repo  create a new AYS repository
  delete       Delete a service and all its children Be...
  destroy      reset in current ays repo all services &...
  discover     Discover AYS repository on the filesystem and...
  do           Schedule an action then immediatly create a...
  install      alias for 'ays do install' make it reality if...
  list         The list command lists all service instances...
  noexec       Enable/Disable the no_exec mode.
  repo_list    List all known repositories
  restore      Use this command when you want to populate...
  run          Look for all action with a state 'schedule',...
  run_info     Print info about run, if not specified will...
  set_state    Manually set the state of an action.
  show         show information about a service
  simulate     is like do only does not execute it, is ideal...
  start        Start the AYS daemon
  state        Print the state of the selected services.
  test         there is a test suite for ays, this command...
  update       Update actor to a new version.
```


```
ays create_repo
```

```
ays blueprint
```

```
ays run
```

```
ays set_state —role <role> —instance<instance> —state new <action>
```

```
ays set_state --role vdc --instance vdc2delete --state new uninstall
```


```
ays run
```

```
ays discover
```

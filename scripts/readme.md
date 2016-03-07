# Usage

```
Usage: cockpit.py install [OPTIONS]

  Start installation process of a new G8Cockpit

Options:
  --repo-url TEXT         Url of the git repository where to store the ays
                          repo.
  --ovc-url TEXT          Url of the Gener8 where to deploy cockpit
  --ovc-login TEXT        Login of your account on Gener8 where to deploy
                          cockpit
  --ovc-password TEXT     Password of your account on the Gener8 where to
                          deploy cockpit
  --ovc-vdc TEXT          Name of the Virtual Data center where to deploy the
                          G8Cockpit
  --ovc-location TEXT     Location of the vdc
  --dns-login TEXT        Password of your account on the Skydns cluster
  --dns-password TEXT     Password of your account on the Skydns cluster
  --dns-name TEXT         Dns to give to the cockpit. Name will be append with
                          .cockpit.aydo.com
  --sshkey TEXT           Path to public ssh key to authorize on the G8Cockpit
  --portal-password TEXT  Admin password of the portal
  --expose-ssh            Expose ssh of the G8Cockpit over HTTP
  --bot-token TEXT        Telegram token of your bot
  --help                  Show this message and exit.

```

You can start the script with all the options filled in like  
`./cockpit.py install --repo-url git@github.com:user/cokpitrepo.git --ovc-url du-conv-1.demo.greenitglobe.com --ovc-login user1 --ovc-password supersecret --ovc-vdc default --dns-login login --dns-password secret --dns-name mycokpit --sshkey /root/.ssh/id_rsa.pub --portal-password secret`

Or you can just run the script without any options and it will interactively ask you the information as the installation is going.
`./cockpit.py install`

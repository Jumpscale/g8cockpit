## Installation using an AYS Blueprint

> Using the **Cockpit Deployer Chatbot** is the recommended way to install a Cockpit.

Below we discuss 5 steps:
- **step 1**: [Preparation](#prep)
- **Step 2**: [Create an AYS service repository](#create-repo)
- **Step 3**: [Create an AYS blueprint for deploying a Cockpit](#create-blueprint)
- **Step 4**: [Execute the blueprint](#execute-blueprint)
- **Step 5**: [Run the install actions](#run-actions)

<a id="prep"></a>
### Step 1: Preparation

Go through the preparation steps as documented [here](/installation/prep/prep.md).

Additionally you will need the private and public key of your DNS server. In the example below we assume you have them available in `/root/.ssh`.


<a id="create-repo"></a>
### Step 2: Create an AYS service repository for your Cockpit

First create your Git repository on the Git server, or on GitHub.

Then create an AYS service repository on your machine using the `ays create_repo` command, specifying your local repository directory and the repository on the Git server:

```
sudo ays create_repo -p {/path/to/my/repo} -g git@github.com:{account}/cockpit_{cockpit-name}.git
```

Or alternatively, you can also do this manually:

```
mkdir -p {/path/to/my/repo}/blueprints
cd {/path/to/my/repo}
touch .ays
git init
vim {/path/to/my/repo}/.git/config
```

Add following configuration:

```
[remote "origin"]
        url = git@github.com:{account}/cockpit_{cockpit-name}.git
        fetch = +refs/heads/*:refs/remotes/origin/*
```

Make sure your Git `user.name` and `user.email` are set:

```
git config --global user.name "{your-full-name}"
git config --global user.email "{your-email-address}"
```

If you're not logged in as root, you will need to reset ownership of the current directory and all subdirectories (recursively) to the currently logged in user, in this case for `cloudscalers`:

```
cd {/path/to/my/repo}
sudo chown -R cloudscalers.cloudscalers .
```

Do your first commit:

```
git add .
git commit -m "first commit"
```

Pull the remote master branch to merge into your local master branch:

```
git pull origin master
```

Push all changes to the server, and since this is your first push you need to specify the up-stream branch you want to push to:

```
git push --set-upstream origin master
```

This will add the following entry to your `.git/config`:

```
[branch "master"]
	remote = origin
	merge = refs/heads/master
```

When you push to a remote and you use the `--set-upstream` flag Git sets the branch you are pushing to as the remote tracking branch of the branch you are pushing.

Adding a remote tracking branch means that Git then knows what you want to do when you git fetch, git pull or git push in future. It assumes that you want to keep the local branch and the remote branch it is tracking in sync and does the appropriate thing to achieve this.


<a id="create-blueprint"></a>
### Step 3: Create an AYS blueprint for deploying a Cockpit

Go to [https://github.com/Jumpscale/jscockpit/tree/8.1.0/blueprint](https://github.com/Jumpscale/jscockpit/tree/8.1.0/blueprint) and copy the example blueprint to your local machine, in a directory that you will use for the Git repository of your new Cockpit:

```
curl https://raw.githubusercontent.com/Jumpscale/jscockpit/8.1.1/blueprint/ovc_blueprint.yaml > {/path/to/my/repo}/blueprints/cockpit_{cockpit-name}.yaml
```





Depending on which platform you install the Cockpit the beginning of the blueprint can different. The only important thing to remember is that the Cockpit service always uses another server of role `node` has parent.
This will indicate to the cockpit on which node it needs to be installed. This bring flexibility during installation cause any service of role `node` can be used.
So you can install a cockpit on top of a VM using `node.ovc`, docker using `node.docker` or any or another node service you would create.

Description of the values for the cockpit service:

```
sshkey__dns:
    key.path: '/root/.ssh/dns_rsa' # this needs to point to the a sshkey authorize on server of our dns infrastructure

# actually install the cockpit
cockpit__main:
   host_node: 'cockpit'
   dns.sshkey: 'dns'
   domain: 'mycockpit.aydo2.com'
   caddy.email: 'me@mail.com'
   caddy.staging: false

   oauth.organization: 'myOrg'
   oauth.client_id: 'myOrg'
   oauth.client_secret: 'replace_me'
   oauth.jwt_key:'MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n27MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny66+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv'
```

- **host_node**: Name of the node service you want to install the cockpit on.
- **dns.sshkey**: Name fo the sshkey servier that point to a sshkey authorize on our DNS infrastructure (dns[1,2,3].aydo.com)
- **domain**:
  - Domain you want for your Cockpit, e.g. `mycockpit.barcelona.aydo.com`
  - If you don't use the auto DNS deployment then make sure your DNS name resolves to the Cockpit IP address
- **caddy.email** : email use for [caddy](https://caddyserver.com/). This email will receive notification when the HTTPS certificate of the cockpit are about to expire. Caddy is supposed to renew them automaticly, but it's always good to double check that it actually happened.
- **oauth.organization**: Name of the organization as set in ItsYou.online, to which you as a user belong to as a member or as an owner; can be the same organization as specified in client_id, but can also be different
- **oauth.client_id**: Name of the organization as set in ItsYou.online, typically the company/organization for which you are setting up the Cockpit; as a user you are not necessairly owner or member of this organization
- **oauth.client_secret**: Client secret for your organization as generated by ItsYou.online
- **oauth.jwt_key**: ItsYou.online public key for JWT signing; see https://github.com/itsyouonline/identityserver/blob/master/docs/oauth2/jwt.md for more details
- **caddy.staging**: (true/false) enable stagging environement of Let's encrypt. Use this when doing test so you don't create real certificate. The number of certificate available for a domain is limited.

<a id="execute-blueprint"></a>
### Step 4: Execute the blueprint

```bash
ays blueprint
```

<a id="run-actions"></a>
### Step 5: Run the install actions

```bash
ays run
```

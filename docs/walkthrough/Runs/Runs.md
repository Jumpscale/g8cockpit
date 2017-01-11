## Runs

The **Runs** page shows all runs for a specific AYS repository.

You get to a **Runs** page from any **Repository Details** page by clicking **Runs** in the navigation menu under **Links**:

![Alt](repoDetails.png)

The **Runs** page lists alls runs, here for the repository `ays_test`:

![Alt](runs.png)

For each run you see the last modification date/time and the current state.

Possible values for **State** are:

- **new** for runs that are still executing
- **ok** for runs that executed successfully
- **error** for runs that have failed

From the **Actions** dropdown you can choose to **Remove all runs in DB**.

Clicking the **Run ID** of a run opens the **Run Details** page, where the steps of the selected run are listed.
Each step of the run can be expanded, showing all the executed jobs. For each job you see the **Actor name**, the **Service Name** and the executed **Action Name**:

![Alt](runDetails.png)

By clicking on the actor name you get to the **Job Details** page, showing you the executed action code and the log file.

![Alt](job.png)


## Using the Cockpit API

Runs can also be retrieved using the Cockpit API, the below will return a JSON object containing all runs:

```
curl -X GET
     -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     http://BASE_URL/ays/repository/REPO_NAME/aysrun
```

Or for run details:

```
curl -X GET
     -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     http://BASE_URL/ays/repository/REPO_NAME/aysrun/RUN_ID
```

In order to use the Cockpit API you first need to obtain an JWT, as documented in the section about [how to get a JWT.](https://github.com/Jumpscale/jscockpit/blob/8.1.1/docs/usage/Howto/Get_JWT/Get_JWT.md).

The authorization header containing the JWT isn't necessary in case of an development installation of the Cockpit.

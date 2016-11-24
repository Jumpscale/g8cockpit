from JumpScale import j

AYS_REPO_DIR = j.sal.fs.joinPaths(j.dirs.varDir, "cockpit_repos")

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

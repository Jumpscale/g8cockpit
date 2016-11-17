from JumpScale import j

AYS_REPO_DIR = j.sal.fs.joinPaths(j.dirs.codeDir, 'cockpit')

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main(j, args, params, tags, tasklet):
    doc = args.doc
    out = []

    account = tags.tagGet('account')
    repo = tags.tagGet('repo')
    provider = tags.tagGet('provider')

    path = j.do.getGitReposListLocal(provider, account, repo)[repo]

    ref = j.clients.git.get(path).getBranchOrTag()
    out.append(ref[1])

    out = '\n'.join(out)

    params.result = (ref[1], doc)
    return params

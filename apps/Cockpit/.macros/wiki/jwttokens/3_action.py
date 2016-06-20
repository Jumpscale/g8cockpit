
def main(j, args, params, tags, tasklet):
    import urllib
    doc = args.doc
    out = list()

    tokens = j.apps.system.oauthtoken.listJWTTokens()
    for token in tokens:
        out.append("{{code:\n%s\n}}" % token['jwt_token'])
    out = '\n'.join(out)
    params.result = (out, doc)

    return params

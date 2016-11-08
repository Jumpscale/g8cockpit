from functools import wraps
from flask import g, request, jsonify


class oauth2_oauth_2_0:

    def __init__(self, scopes=None):

        self.described_by = "headers"
        self.field = "Authorization"

        self.allowed_scopes = scopes

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = ""
            if self.described_by == "headers":
                token = request.headers.get(self.field, "")
            elif self.described_by == "queryParameters":
                token = request.args.get("access_token", "")

            if token == "":
                return jsonify(), 401

            g.access_token = token

            # provide code to check scopes of the access_token
            scopes = []

            if self.check_scopes(scopes) == False:
                return jsonify(), 403
            return f(*args, **kwargs)
        return decorated_function

    def check_scopes(self, scopes):
        if self.allowed_scopes is None or len(self.allowed_scopes) == 0:
            return True

        for allowed in self.allowed_scopes:
            for s in scopes:
                if s == allowed:
                    return True

        return False

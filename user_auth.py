import tekore as tk

CONF = tk.config_from_environment()
CRED = tk.Credentials(*CONF)
SCOPES = tk.scope.every

auths = {}  # Ongoing authorisations: UserAuth.state(user ID) -> UserAuth


def refresh_token(token):
    """:returns refreshed token"""
    return CRED.refresh(token)


class UserAuth(tk.UserAuth):
    """tekore.UserAuth, implement user authorisation flow"""

    def __init__(self):
        super().__init__(cred=CRED, scope=SCOPES)

    def get_token(self, code, state):
        """:returns spotify user token, using 'code' and 'state' redirect parameters"""
        return self.request_token(code=code, state=state)

from social_core.backends.oauth import BaseOAuth2PKCE


class ZaloOAuth2(BaseOAuth2PKCE):
    """Zalo Social API OAuth v4 backend with state validation and PKCE."""

    name = "zalo"
    ID_KEY = "id"
    AUTHORIZATION_URL = "https://oauth.zaloapp.com/v4/permission"
    ACCESS_TOKEN_URL = "https://oauth.zaloapp.com/v4/access_token"
    USER_DATA_URL = "https://graph.zalo.me/v2.0/me"
    ACCESS_TOKEN_METHOD = "POST"
    REDIRECT_STATE = False

    def auth_params(self, state=None):
        params = super().auth_params(state=state)
        params["app_id"] = params.pop("client_id")
        # Zalo uses its configured callback URL and PKCE S256 challenge.
        params.pop("response_type", None)
        params.pop("code_challenge_method", None)
        return params

    def auth_complete_params(self, state=None):
        params = super().auth_complete_params(state=state)
        params["app_id"] = params.pop("client_id")
        params.pop("client_secret", None)
        params.pop("redirect_uri", None)
        return params

    def auth_headers(self):
        headers = super().auth_headers()
        _app_id, app_secret = self.get_key_and_secret()
        headers["secret_key"] = app_secret
        return headers

    def get_user_details(self, response):
        zalo_id = response.get("id")
        if not zalo_id:
            return {}

        display_name = (response.get("name") or "").strip()
        return {
            "username": f"zalo_{zalo_id}",
            "email": "",
            "fullname": display_name,
        }

    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(
            self.USER_DATA_URL,
            headers={"access_token": access_token},
            params={"fields": "id,name,picture"},
        )
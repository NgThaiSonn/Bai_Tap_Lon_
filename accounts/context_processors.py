from django.conf import settings


def social_login_options(request):
    """Expose only providers with both credentials configured."""
    return {
        "social_login_providers": {
            "google": bool(
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
                and settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
            ),
            "facebook": bool(
                settings.SOCIAL_AUTH_FACEBOOK_KEY
                and settings.SOCIAL_AUTH_FACEBOOK_SECRET
            ),
            "zalo": bool(
                settings.SOCIAL_AUTH_ZALO_KEY and settings.SOCIAL_AUTH_ZALO_SECRET
            ),
        }
    }
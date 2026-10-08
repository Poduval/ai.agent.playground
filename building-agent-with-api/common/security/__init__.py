"""Authentication helpers for the REST API and the A2A agent."""

from common.security.auth import BearerTokenMiddleware, api_key_auth

__all__ = ["BearerTokenMiddleware", "api_key_auth"]

# Auth Service

Multi-channel authentication for the loan platform. One service, several
pluggable **channels**, a uniform token contract.

## Channels

Each channel implements the `AuthChannel` protocol in
[`channels/base.py`](channels/base.py):

| Channel          | Module                       | Identifier        |
| ---------------- | ---------------------------- | ----------------- |
| Email + password | `channels/email_password.py` | `email_password`  |
| OTP over SMS     | `channels/otp_sms.py`        | `otp_sms`         |
| Google OAuth 2.0 | `channels/oauth_google.py`   | `oauth_google`    |
| Magic link       | `channels/magic_link.py`     | `magic_link`      |

Add a channel by dropping a new module in `channels/` that implements the
protocol and registering its identifier - no other service is touched.

## Tokens

- `tokens/jwt.py` - short-lived JWT **access** tokens.
- `tokens/refresh.py` - opaque, rotating **refresh** tokens backed by a `Session`.

## Endpoints

| Method | Path            | Purpose                      |
| ------ | --------------- | ---------------------------- |
| POST   | `/auth/login`   | Authenticate via a channel.  |
| POST   | `/auth/refresh` | Rotate a refresh token.      |
| POST   | `/auth/logout`  | Revoke the current session.  |

## Configuration

`AuthSettings` (`AUTH_` env prefix) in [`config.py`](config.py): JWT secret /
algorithm, access & refresh TTLs, and (later) provider credentials. Never bake
secrets into the image - supply them via env or a secret manager.

## Models

`User`, `Credential` (per-channel), and `Session` (refresh-token-backed) in
[`models.py`](models.py).

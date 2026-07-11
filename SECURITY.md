# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Boilerworks, please report it responsibly.

**Do not open a public issue.**

Instead, email **security@weareconflict.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and aim to release a fix within 7 days for critical issues.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| latest  | Yes       |

## Security Best Practices

When deploying a service built from this template:

- Change the default Postgres credentials — the `postgres:postgres` values in `docker-compose.yaml` and the default `DATABASE_URL` are dev-only
- Set `DEBUG=false` in production — this disables `/docs` and `/redoc` and prevents exception details from leaking in 500 responses
- Use HTTPS in production (terminate TLS at your reverse proxy or load balancer)
- Treat API keys as secrets: the raw key is returned once at creation and only its SHA256 hash is stored — rotate by creating a new key, then revoking the old one via `DELETE /api-keys/{id}`
- Never commit `.env` (it is gitignored) — use `.env.example` as the reference

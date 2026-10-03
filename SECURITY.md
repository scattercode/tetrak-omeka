# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately through GitHub's
[private vulnerability reporting](https://github.com/scattercode/tetrak-omeka/security/advisories/new)
(Security tab → "Report a vulnerability"). Do not open a public issue for a
security problem.

We aim to acknowledge reports within seven days. This is a small
collaborative project, not a company with a security team, but we take
reports seriously and will keep you informed as we investigate.

## Scope

This is a local demo, not a deployment. The stack binds to `127.0.0.1`, and
the credentials in `.env.example` are local scaffolding, not secrets. Do not
expose it to a network or put sensitive material in it.

Vulnerabilities in Omeka S itself belong with the Omeka project; we pin a
release and apply its fixes by upgrading.

## What we do ourselves

- Omeka is built from the official release, pinned by version and SHA-256,
  and the image applies Debian's security fixes at build time.
- Trivy scans the built image and the Dockerfile and compose configuration on
  every pull request, and the images again weekly; Dependabot keeps the base
  images and workflow actions current.

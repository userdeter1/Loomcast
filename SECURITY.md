
# Security Policy

## Supported versions

Loomcast is pre-1.0. Only the latest released version receives security fixes.

| Version | Supported |
| ------- | --------- |
| 0.1.x   | ✅        |
| < 0.1   | ❌        |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately through GitHub:
[Report a vulnerability](https://github.com/userdeter1/Loomcast/security/advisories/new)

Include the affected version, reproduction steps, and the impact you observed.
You can expect an initial response within 7 days.

## Scope

Loomcast is a client library and CLI. It runs entirely inside the calling
process and opens no listening port of its own. It talks to LLM runtimes
(Ollama, LM Studio, llama.cpp) that you start and control yourself, and it
fetches the model catalog over HTTPS from `ollama.com`.

Relevant to security reports:

- The static catalog shipped in the package is verified against a SHA-256
  checksum at load time.
- The dynamic catalog scrapes a remote page. Malformed or hostile content
  must degrade to the bundled static catalog rather than propagate.
- Loomcast never executes model content and never writes outside its
  platform-specific config and cache directories.

Out of scope: vulnerabilities in the LLM runtimes themselves, and the content
or behaviour of the models you choose to download.

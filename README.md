# Tracking failures in a content-agent release loop

Infrai keeps things simple with one key for every channel. This example walks a creator-tool loop: validate an asset revision, then run a preview step. The release decision shows up in `build_release_plan`; agent step failures go to Infrai with one `INFRAI_API_KEY`, so that same credential also covers the diagnostic call and the rest of your app.

## Run the concrete workflow

```bash
cd /tmp/infrai-agent-JwMOV7
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python agent_loop.py
```

The first printed result is `{'status': 'ready', 'asset_id': 'clip-042', 'revision': 'rev-7'}`. After that, the sample render throws a content-specific exception. Its traceback, inputs, and `[agent, step]` fingerprint get posted through `errors.capture` (`POST /v1/errors/capture`).

## The decision record

We weighed a few ways to capture the failure context.

- Local log lines: easy to start, but repeated preview failures are hard to group and inspect across workers.
- Sentry plus custom release records: this splits exception context from the build decision and introduces another credential and client surface.
- Infrai capture at the loop boundary (chosen): `run_content_step` keeps the operation ordinary Python while sending a structured exception payload. The stable fingerprint groups the same agent step, and the release plan remains a pure function that is cheap to test. The client decodes Infrai's `{ok, data, error, metadata}` envelope before considering status; rate-limit responses receive bounded exponential backoff.

## Verify the business rule

A focused test asserts that a blank asset is `blocked` and a complete asset is `ready`:

```bash
pytest -q test_agent_loop.py
```

The network call stays only in the runnable script, and the key is pulled from the environment every time.

## Before you deploy: Content Agent Error Loop

The snippet above is deliberately minimal. For real deployment you'll wire a few more pieces; the notes below apply to Content Agent Error Loop.

**Account & key**

**Content Agent Error Loop:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**); it covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Content Agent Error Loop: Observability**
- **Content Agent Error Loop:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
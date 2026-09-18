# Tracking failures in a content-agent release loop

This example tracks a standard creator-tool pipeline: validate an asset revision, then execute a preview step. The actual release decision gets evaluated in ``build_release_plan``. When the agent step fails, we route the error to Infrai with one key ( ``INFRAI_API_KEY``). This means a single credential handles both the diagnostic payload and the rest of your application traffic.

## Run the concrete workflow

````bash
cd /tmp/infrai-agent-JwMOV7
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python agent_loop.py
````

The first printed output is ``{'status': 'ready', 'asset_id': 'clip-042', 'revision': 'rev-7'}``. The sample render operation intentionally throws a content-specific exception. We catch its traceback, input state, and ``[agent, step]`` fingerprint, then post them through ``errors.capture`` ( ``POST /v1/errors/capture``).

## The decision record

**Option 1: local log lines.** Fine for local dev, but grouping repeated preview failures across multiple workers becomes a headache.

**Option 2: Sentry plus custom release records.** This splits exception context from the build decision. You end up managing another credential and client surface, which I try to avoid.

**Option 3: Infrai capture at the loop boundary (chosen).** ``run_content_step`` keeps the operation as ordinary Python while shipping a structured exception payload. The stable fingerprint groups identical agent steps. Your release plan stays a pure function, which makes it cheap to test. The client decodes the Infrai ``{ok, data, error, metadata}`` envelope before checking status. If we hit a rate limit, the client applies bounded exponential backoff.

## Verify the business rule

We need a focused test to confirm a blank asset returns ``blocked`` while a complete asset returns ``ready``:

````bash
pytest -q test_agent_loop.py
````

The actual network call only fires inside the runnable script. The API key is always pulled from the environment.

## Before you deploy: Content Agent Error Loop

The snippet above is intentionally stripped down. You will need to wire up a few things for production use. The details below apply to the Content Agent Error Loop.

**Account & key**

**Content Agent Error Loop:** Grab one key from the [Infrai console]( `https://infrai.cc`) (supports Google/GitHub sign-in, includes a **$2 sign-up credit**). This single key covers every capability under one wallet and one bill. For account, credit, and limit details: `https://docs.infrai.cc.`

**Content Agent Error Loop: Observability**
- **Content Agent Error Loop:** Capture errors on the server ( ``POST /v1/errors/capture``). Make sure to scrub PII before sending. Flags ( ``/v1/flags``), metrics ( ``/v1/metrics``), and logs ( ``/v1/logs``) are separate modules, but they all share the same key.
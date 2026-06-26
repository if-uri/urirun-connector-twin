# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/if-uri/urirun-connector-twin
- **Primary Language**: python
- **Languages**: python: 10, yaml: 4, shell: 2, json: 1, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 94
- **Total Classes**: 1
- **Modules**: 18
- **Entry Points**: 24

## Architecture by Module

### urirun_connector_twin.core
- **Functions**: 26
- **File**: `core.py`

### urirun_connector_twin.prompt_plan
- **Functions**: 18
- **File**: `prompt_plan.py`

### urirun_connector_twin.browser
- **Functions**: 11
- **File**: `browser.py`

### urirun_connector_twin.session
- **Functions**: 9
- **File**: `session.py`

### urirun_connector_twin.sandbox
- **Functions**: 8
- **Classes**: 1
- **File**: `sandbox.py`

### urirun_connector_twin.environment
- **Functions**: 8
- **File**: `environment.py`

### urirun_connector_twin.planner
- **Functions**: 7
- **File**: `planner.py`

### urirun_connector_twin.mock
- **Functions**: 4
- **File**: `mock.py`

### urirun_connector_twin.dispatch
- **Functions**: 3
- **File**: `dispatch.py`

## Key Entry Points

Main execution flows into the system:

### urirun_connector_twin.core.plan_from_prompt_route
> Full twin loop from a single NL prompt.

Calls twin://host/browser/query/profile via the mesh (switchable URI) with
fallback to local browser.py scan.
- **Calls**: conn.handler, urirun_connector_twin.session.derive_task_target, urirun_connector_twin.prompt_plan.plan_from_prompt, urirun_connector_twin.dispatch.uri_call, urirun_connector_twin.dispatch.uri_call, urirun_connector_twin.core._prompt_result, urirun_connector_twin.dispatch.value_of, urirun_connector_twin.environment.probe

### urirun_connector_twin.core.mock_start_probe_stop
> Close the mock ↔ sandbox loop: generate → up → health-check → down -v.

Proves that the generated Docker mock is:
  - reachable (HTTP 200 on testUri w
- **Calls**: conn.handler, urirun_connector_twin.environment.probe, urirun_connector_twin.planner.build_imperative_plan, urirun_connector_twin.mock.generate_mock, tempfile.mkdtemp, urirun.ok, mock.get, shutil.which

### urirun_connector_twin.core.flow_preflight
> Identify which surfaces the flow steps need and provision them up-front.

For CDP-dependent steps: if CDP is feasible but not reachable on the target

- **Calls**: conn.handler, sorted, urirun.ok, timeline.append, _svc.call, bool, provisioned.append, len

### urirun_connector_twin.core.browser_profile
> Select the best live Chrome session for a domain or natural language task.

Priority: auth cookie confirmed > tab on domain > real profile > any reach
- **Calls**: conn.handler, urirun_connector_twin.browser.discover_browser_sessions, urirun_connector_twin.browser.select_session, urirun.ok, urirun_connector_twin.session.derive_task_target, t.get, bool, t.get

### urirun_connector_twin.core.step_feasibility
> Check whether a single URI step is feasible on the current node.
- **Calls**: conn.handler, urirun_connector_twin.environment.probe, urirun_connector_twin.planner.annotate_steps, urirun.ok, env.get, s.get, s.get, s.get

### urirun_connector_twin.core.flow_rollback
> Undo reversible mutations from a pre-built thin-driver ledger (LIFO).

Each entry: {uri, inverse, args, before, after}.  Applies inverses in reverse
o
- **Calls**: conn.handler, reversed, urirun.ok, urirun.ok, entry.get, undone.append, _svc.call, rb.get

### urirun_connector_twin.core.step_evaluate
> Retry/heal/rollback decision for a single failed flow step.

Makes the decision observable and switchable: callers replace this URI
to inject differen
- **Calls**: conn.handler, can_retry_step, urirun.ok, entry.get, urirun.ok, diagnosis.get, None.get, urirun.ok

### urirun_connector_twin.session.probe_session
> Enrich a session entry with reachability, tabs, and auth state.
- **Calls**: urirun_connector_twin.session._cdp_pages, bool, bool, tab.get, p.get, p.get, p.get, urirun_connector_twin.session._check_auth_cookies

### urirun_connector_twin.core.mock_create
> Generate a reversible Docker Compose environment for testing infeasible steps.
- **Calls**: conn.handler, urirun_connector_twin.environment.probe, urirun_connector_twin.planner.build_imperative_plan, urirun_connector_twin.mock.generate_mock, urirun.ok, mock.get, mock.get

### urirun_connector_twin.core.flow_goal_verify
> Check goal end-state after a flow.

Calls goal.uri via the mesh and asserts the goal condition (contains/equals/present).
Returns {ok:True, goalMet:Tr
- **Calls**: conn.handler, goal.get, urirun.ok, _svc.call, _run_goal_check, urirun.ok, str

### urirun_connector_twin.core.browser_sessions
> Enumerate debug-enabled Chrome/Chromium processes on this host.

probe_cookies=True: reads Network.getAllCookies per session (slower, auth proof).
pro
- **Calls**: conn.handler, urirun_connector_twin.browser.discover_browser_sessions, urirun.ok, len, sum, s.get

### urirun_connector_twin.session.discover_browser_sessions
> Return metadata for every live debug-enabled Chrome process on this host.
- **Calls**: set, urirun_connector_twin.session._proc_cmdlines, urirun_connector_twin.session._extract_chrome_info, seen_ports.add, sessions.append

### urirun_connector_twin.session.select_best_session
> Choose the session to use for a given task.

Priority:
  1. Session with authConfirmed (proven login via auth cookie) on target domain
  2. Session wi
- **Calls**: task.get, task.get, s.get, s.get, s.get

### urirun_connector_twin.core.constraints_from_profile
> Derive per-action infeasibility constraints from a kvm actionMatrix.

URI boundary between 'what surfaces exist' (kvm data) and 'which actions are
blo
- **Calls**: conn.handler, urirun_connector_twin.core._safe_import, urirun.ok, urirun.ok, rev._infeasible_constraints

### urirun_connector_twin.core.plan_generate
> Annotate a pre-built urirun flow with feasibility, reversibility and surface.
- **Calls**: conn.handler, urirun_connector_twin.environment.probe, urirun_connector_twin.planner.build_imperative_plan, plan.get, urirun_connector_twin.mock.generate_mock

### urirun_connector_twin.core.sandbox_probe
> Run scan(before) → forward → scan(after) → inverse → scan(restored).

reversible := before == restored  AND  before != after.

When `uri` is given and
- **Calls**: conn.handler, urirun_connector_twin.sandbox.probe_reversibility, urirun_connector_twin.sandbox.scenario_for_uri, Scenario

### urirun_connector_twin.core.environment_profile
> Collect a structured capability snapshot for the given node (or localhost).
- **Calls**: conn.handler, urirun_connector_twin.environment.probe, urirun.ok

### urirun_connector_twin.core.plan_annotate
> URI boundary for build_imperative_plan — switchable annotation logic.

Deploying a different twin connector with a smarter annotator (e.g. LLM-augment
- **Calls**: conn.handler, urirun_connector_twin.planner.build_imperative_plan, urirun.ok

### urirun_connector_twin.core.monitor_event
> Receive a twin state-transition event (distributed to /events?scheme=twin SSE).
- **Calls**: conn.handler, urirun.ok

### urirun_connector_twin.core.manifest
- **Calls**: conn.manifest, urirun.load_manifest

### urirun_connector_twin.core.main
- **Calls**: conn.cli, urirun.load_manifest

### urirun_connector_twin.core.bindings
- **Calls**: conn.bindings

### urirun_connector_twin.dispatch.set_transport
> Inject a transport fn(uri, payload) -> dict used before v2_service.

Pass None to clear.  Used by tests to stub URI calls and by the node
runner to bi

### urirun_connector_twin.prompt_plan._file_write_steps

## Process Flows

Key execution flows identified:

### Flow 1: plan_from_prompt_route
```
plan_from_prompt_route [urirun_connector_twin.core]
  └─ →> derive_task_target
  └─ →> plan_from_prompt
      └─> derive_task_target
          └─> _extract_domain
          └─> _extract_url
  └─ →> uri_call
```

### Flow 2: mock_start_probe_stop
```
mock_start_probe_stop [urirun_connector_twin.core]
  └─ →> probe
      └─> _host_os_info
      └─> _constraints_via_uri
          └─> _constraints_from_profile_local
  └─ →> build_imperative_plan
      └─> extract_steps_from_flow
      └─> annotate_steps
          └─> _is_infeasible
  └─ →> generate_mock
      └─> _resolve_service
          └─> _detect_service
      └─> _compose_yaml
```

### Flow 3: flow_preflight
```
flow_preflight [urirun_connector_twin.core]
```

### Flow 4: browser_profile
```
browser_profile [urirun_connector_twin.core]
  └─ →> discover_browser_sessions
      └─> _proc_cmdline
      └─> _extract_flag
  └─ →> select_session
      └─> _domain_key
      └─> _selection
  └─ →> derive_task_target
```

### Flow 5: step_feasibility
```
step_feasibility [urirun_connector_twin.core]
  └─ →> probe
      └─> _host_os_info
      └─> _constraints_via_uri
          └─> _constraints_from_profile_local
  └─ →> annotate_steps
      └─> _is_infeasible
          └─> _route_suffix
```

### Flow 6: flow_rollback
```
flow_rollback [urirun_connector_twin.core]
```

### Flow 7: step_evaluate
```
step_evaluate [urirun_connector_twin.core]
```

### Flow 8: probe_session
```
probe_session [urirun_connector_twin.session]
  └─> _cdp_pages
```

### Flow 9: mock_create
```
mock_create [urirun_connector_twin.core]
  └─ →> probe
      └─> _host_os_info
      └─> _constraints_via_uri
          └─> _constraints_from_profile_local
  └─ →> build_imperative_plan
      └─> extract_steps_from_flow
      └─> annotate_steps
          └─> _is_infeasible
  └─ →> generate_mock
      └─> _resolve_service
          └─> _detect_service
      └─> _compose_yaml
```

### Flow 10: flow_goal_verify
```
flow_goal_verify [urirun_connector_twin.core]
```

## Key Classes

### urirun_connector_twin.sandbox.Scenario
> One reversibility experiment.

Every *_cmd is a POSIX sh command executed inside the sandbox (contai
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### urirun_connector_twin.sandbox._parse_sections
- **Output to**: _between, _between, None.strip, None.strip, raw.split

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `urirun_connector_twin.core.plan_from_prompt_route` - 18 calls
- `urirun_connector_twin.browser.discover_browser_sessions` - 17 calls
- `urirun_connector_twin.environment.probe` - 17 calls
- `urirun_connector_twin.core.mock_start_probe_stop` - 16 calls
- `urirun_connector_twin.planner.build_imperative_plan` - 14 calls
- `urirun_connector_twin.prompt_plan.steps_from_prompt` - 14 calls
- `urirun_connector_twin.core.flow_preflight` - 14 calls
- `urirun_connector_twin.planner.annotate_steps` - 13 calls
- `urirun_connector_twin.prompt_plan.derive_task_target` - 12 calls
- `urirun_connector_twin.core.browser_profile` - 12 calls
- `urirun_connector_twin.core.step_feasibility` - 12 calls
- `urirun_connector_twin.browser.select_session` - 11 calls
- `urirun_connector_twin.core.flow_rollback` - 11 calls
- `urirun_connector_twin.core.step_evaluate` - 11 calls
- `urirun_connector_twin.session.probe_session` - 9 calls
- `urirun_connector_twin.core.mock_create` - 7 calls
- `urirun_connector_twin.core.flow_goal_verify` - 7 calls
- `urirun_connector_twin.mock.generate_mock` - 6 calls
- `urirun_connector_twin.core.browser_sessions` - 6 calls
- `urirun_connector_twin.dispatch.uri_call` - 5 calls
- `urirun_connector_twin.session.discover_browser_sessions` - 5 calls
- `urirun_connector_twin.session.select_best_session` - 5 calls
- `urirun_connector_twin.core.constraints_from_profile` - 5 calls
- `urirun_connector_twin.core.plan_generate` - 5 calls
- `urirun_connector_twin.sandbox.probe_reversibility` - 4 calls
- `urirun_connector_twin.dispatch.value_of` - 4 calls
- `urirun_connector_twin.planner.extract_steps_from_flow` - 4 calls
- `urirun_connector_twin.core.sandbox_probe` - 4 calls
- `urirun_connector_twin.sandbox.scenario_for_uri` - 3 calls
- `urirun_connector_twin.prompt_plan.plan_from_prompt` - 3 calls
- `urirun_connector_twin.core.environment_profile` - 3 calls
- `urirun_connector_twin.core.plan_annotate` - 3 calls
- `urirun_connector_twin.session.derive_task_target` - 2 calls
- `urirun_connector_twin.core.monitor_event` - 2 calls
- `urirun_connector_twin.core.manifest` - 2 calls
- `urirun_connector_twin.core.main` - 2 calls
- `urirun_connector_twin.core.bindings` - 1 calls
- `urirun_connector_twin.dispatch.set_transport` - 0 calls

## System Interactions

How components interact:

```mermaid
graph TD
    plan_from_prompt_rou --> handler
    plan_from_prompt_rou --> derive_task_target
    plan_from_prompt_rou --> plan_from_prompt
    plan_from_prompt_rou --> uri_call
    mock_start_probe_sto --> handler
    mock_start_probe_sto --> probe
    mock_start_probe_sto --> build_imperative_pla
    mock_start_probe_sto --> generate_mock
    mock_start_probe_sto --> mkdtemp
    flow_preflight --> handler
    flow_preflight --> sorted
    flow_preflight --> ok
    flow_preflight --> append
    flow_preflight --> call
    browser_profile --> handler
    browser_profile --> discover_browser_ses
    browser_profile --> select_session
    browser_profile --> ok
    browser_profile --> derive_task_target
    step_feasibility --> handler
    step_feasibility --> probe
    step_feasibility --> annotate_steps
    step_feasibility --> ok
    step_feasibility --> get
    flow_rollback --> handler
    flow_rollback --> reversed
    flow_rollback --> ok
    flow_rollback --> get
    step_evaluate --> handler
    step_evaluate --> can_retry_step
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.
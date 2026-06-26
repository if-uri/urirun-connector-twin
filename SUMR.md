# urirun-connector-twin

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `urirun-connector-twin`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: urirun-connector-twin;
  version: 0.1.0;
}

dependencies {
  runtime: "urirun @ git+https://github.com/if-uri/urirun.git#subdirectory=adapters/python";
  test: pytest>=8;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="urirun-connector-twin"] {
  entry: urirun_connector_twin.core:main;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  python_version: >=3.10;
}
```

## Dependencies

### Runtime

```text markpact:deps python
urirun @ git+https://github.com/if-uri/urirun.git#subdirectory=adapters/python
```

## Call Graph

*76 nodes · 94 edges · 8 modules · CC̄=4.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_cdp_cookies` *(in urirun_connector_twin.browser)* | 13 ⚠ | 1 | 32 | **33** |
| `probe` *(in urirun_connector_twin.environment)* | 11 ⚠ | 7 | 17 | **24** |
| `discover_browser_sessions` *(in urirun_connector_twin.browser)* | 15 ⚠ | 4 | 17 | **21** |
| `build_imperative_plan` *(in urirun_connector_twin.planner)* | 8 | 6 | 14 | **20** |
| `plan_from_prompt_route` *(in urirun_connector_twin.core)* | 13 ⚠ | 0 | 18 | **18** |
| `mock_start_probe_stop` *(in urirun_connector_twin.core)* | 7 | 0 | 16 | **16** |
| `annotate_steps` *(in urirun_connector_twin.planner)* | 8 | 2 | 13 | **15** |
| `select_session` *(in urirun_connector_twin.browser)* | 15 ⚠ | 3 | 11 | **14** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/if-uri/urirun-connector-twin
# generated in 0.03s
# nodes: 76 | edges: 94 | modules: 8
# CC̄=4.1

HUBS[20]:
  urirun_connector_twin.browser._cdp_cookies
    CC=13  in:1  out:32  total:33
  urirun_connector_twin.environment.probe
    CC=11  in:7  out:17  total:24
  urirun_connector_twin.browser.discover_browser_sessions
    CC=15  in:4  out:17  total:21
  urirun_connector_twin.planner.build_imperative_plan
    CC=8  in:6  out:14  total:20
  urirun_connector_twin.core.plan_from_prompt_route
    CC=13  in:0  out:18  total:18
  urirun_connector_twin.core.mock_start_probe_stop
    CC=7  in:0  out:16  total:16
  urirun_connector_twin.planner.annotate_steps
    CC=8  in:2  out:13  total:15
  urirun_connector_twin.browser.select_session
    CC=15  in:3  out:11  total:14
  urirun_connector_twin.core.flow_preflight
    CC=9  in:0  out:14  total:14
  urirun_connector_twin.sandbox._simulated_probe
    CC=1  in:1  out:12  total:13
  urirun_connector_twin.core.browser_profile
    CC=7  in:0  out:12  total:12
  urirun_connector_twin.prompt_plan._raw_steps_for_target
    CC=13  in:1  out:11  total:12
  urirun_connector_twin.core.step_feasibility
    CC=4  in:0  out:12  total:12
  urirun_connector_twin.core._prompt_result
    CC=5  in:1  out:11  total:12
  urirun_connector_twin.dispatch.uri_call
    CC=10  in:6  out:5  total:11
  urirun_connector_twin.prompt_plan.derive_task_target
    CC=2  in:5  out:6  total:11
  urirun_connector_twin.browser._selection
    CC=6  in:3  out:7  total:10
  urirun_connector_twin.mock.generate_mock
    CC=5  in:4  out:6  total:10
  urirun_connector_twin.prompt_plan._extract_text_to_type
    CC=5  in:1  out:8  total:9
  urirun_connector_twin.sandbox._parse_sections
    CC=2  in:1  out:7  total:8

MODULES:
  urirun_connector_twin.browser  [11 funcs]
    _cdp_cookies  CC=13  out:32
    _cdp_pages  CC=2  out:4
    _domain_key  CC=3  out:3
    _extract_chrome_info  CC=5  out:4
    _extract_flag  CC=3  out:3
    _is_browser  CC=3  out:3
    _port_open  CC=2  out:1
    _proc_cmdline  CC=2  out:4
    _selection  CC=6  out:7
    discover_browser_sessions  CC=15  out:17
  urirun_connector_twin.core  [17 funcs]
    _local_browser_profile  CC=1  out:3
    _prompt_result  CC=5  out:11
    _run_compose  CC=4  out:2
    _safe_import  CC=3  out:2
    _target_of  CC=2  out:2
    browser_profile  CC=7  out:12
    browser_sessions  CC=3  out:6
    constraints_from_profile  CC=4  out:5
    environment_profile  CC=2  out:3
    flow_preflight  CC=9  out:14
  urirun_connector_twin.dispatch  [2 funcs]
    uri_call  CC=10  out:5
    value_of  CC=4  out:4
  urirun_connector_twin.environment  [7 funcs]
    _constraints_from_profile_local  CC=3  out:2
    _constraints_via_uri  CC=3  out:4
    _host_os_info  CC=1  out:7
    _kvm_query  CC=4  out:3
    _probe_browser  CC=5  out:6
    _safe_import  CC=3  out:2
    probe  CC=11  out:17
  urirun_connector_twin.mock  [4 funcs]
    _compose_yaml  CC=3  out:3
    _detect_service  CC=3  out:2
    _resolve_service  CC=5  out:2
    generate_mock  CC=5  out:6
  urirun_connector_twin.planner  [7 funcs]
    _is_infeasible  CC=5  out:3
    _route_suffix  CC=2  out:4
    _step_reversible  CC=3  out:2
    _step_surface  CC=7  out:3
    annotate_steps  CC=8  out:13
    build_imperative_plan  CC=8  out:14
    extract_steps_from_flow  CC=4  out:4
  urirun_connector_twin.prompt_plan  [20 funcs]
    _bind_node  CC=1  out:1
    _browser_fill_and_submit_steps  CC=1  out:1
    _browser_open_steps  CC=1  out:0
    _classify_task_type  CC=6  out:2
    _extract_domain  CC=5  out:4
    _extract_query  CC=3  out:5
    _extract_text_to_type  CC=5  out:8
    _extract_url  CC=2  out:2
    _fallback_describe_steps  CC=1  out:0
    _guess_service_name  CC=2  out:3
  urirun_connector_twin.sandbox  [8 funcs]
    _docker_available  CC=1  out:1
    _docker_probe  CC=1  out:5
    _parse_sections  CC=2  out:7
    _run  CC=4  out:2
    _simulated_probe  CC=1  out:12
    _verdict  CC=4  out:0
    probe_reversibility  CC=2  out:4
    scenario_for_uri  CC=6  out:3

EDGES:
  urirun_connector_twin.sandbox._docker_probe → urirun_connector_twin.sandbox._run
  urirun_connector_twin.sandbox._docker_probe → urirun_connector_twin.sandbox._parse_sections
  urirun_connector_twin.sandbox._docker_probe → urirun_connector_twin.sandbox._verdict
  urirun_connector_twin.sandbox._simulated_probe → urirun_connector_twin.sandbox._run
  urirun_connector_twin.sandbox.probe_reversibility → urirun_connector_twin.sandbox._docker_available
  urirun_connector_twin.sandbox.probe_reversibility → urirun_connector_twin.sandbox._docker_probe
  urirun_connector_twin.sandbox.probe_reversibility → urirun_connector_twin.sandbox._simulated_probe
  urirun_connector_twin.mock._resolve_service → urirun_connector_twin.mock._detect_service
  urirun_connector_twin.mock.generate_mock → urirun_connector_twin.mock._resolve_service
  urirun_connector_twin.mock.generate_mock → urirun_connector_twin.mock._compose_yaml
  urirun_connector_twin.browser._cdp_cookies → urirun_connector_twin.browser._cdp_pages
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._proc_cmdline
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._extract_flag
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._port_open
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._is_browser
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._cdp_pages
  urirun_connector_twin.browser.select_session → urirun_connector_twin.browser._domain_key
  urirun_connector_twin.browser.select_session → urirun_connector_twin.browser._selection
  urirun_connector_twin.browser._extract_chrome_info → urirun_connector_twin.browser._extract_flag
  urirun_connector_twin.browser._extract_chrome_info → urirun_connector_twin.browser._is_browser
  urirun_connector_twin.planner._is_infeasible → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner._step_surface → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner._step_reversible → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._is_infeasible
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._step_reversible
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._step_surface
  urirun_connector_twin.planner.build_imperative_plan → urirun_connector_twin.planner.extract_steps_from_flow
  urirun_connector_twin.planner.build_imperative_plan → urirun_connector_twin.planner.annotate_steps
  urirun_connector_twin.core._local_browser_profile → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core._local_browser_profile → urirun_connector_twin.browser.select_session
  urirun_connector_twin.core._prompt_result → urirun_connector_twin.mock.generate_mock
  urirun_connector_twin.core.environment_profile → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.constraints_from_profile → urirun_connector_twin.core._safe_import
  urirun_connector_twin.core.browser_sessions → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core.browser_profile → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core.browser_profile → urirun_connector_twin.browser.select_session
  urirun_connector_twin.core.browser_profile → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.prompt_plan.plan_from_prompt
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.dispatch.uri_call
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.core._prompt_result
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.dispatch.value_of
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.plan_annotate → urirun_connector_twin.planner.build_imperative_plan
  urirun_connector_twin.core.plan_generate → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.plan_generate → urirun_connector_twin.planner.build_imperative_plan
  urirun_connector_twin.core.plan_generate → urirun_connector_twin.mock.generate_mock
  urirun_connector_twin.core.mock_create → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.mock_create → urirun_connector_twin.planner.build_imperative_plan
  urirun_connector_twin.core.mock_create → urirun_connector_twin.mock.generate_mock
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**
- assert `inverse_calls == ["inverse-b"`
- assert `inverse_calls == ["inverse-b"`

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/if-uri/urirun-connector-twin
# generated in 0.03s
# nodes: 76 | edges: 94 | modules: 8
# CC̄=4.1

HUBS[20]:
  urirun_connector_twin.browser._cdp_cookies
    CC=13  in:1  out:32  total:33
  urirun_connector_twin.environment.probe
    CC=11  in:7  out:17  total:24
  urirun_connector_twin.browser.discover_browser_sessions
    CC=15  in:4  out:17  total:21
  urirun_connector_twin.planner.build_imperative_plan
    CC=8  in:6  out:14  total:20
  urirun_connector_twin.core.plan_from_prompt_route
    CC=13  in:0  out:18  total:18
  urirun_connector_twin.core.mock_start_probe_stop
    CC=7  in:0  out:16  total:16
  urirun_connector_twin.planner.annotate_steps
    CC=8  in:2  out:13  total:15
  urirun_connector_twin.browser.select_session
    CC=15  in:3  out:11  total:14
  urirun_connector_twin.core.flow_preflight
    CC=9  in:0  out:14  total:14
  urirun_connector_twin.sandbox._simulated_probe
    CC=1  in:1  out:12  total:13
  urirun_connector_twin.core.browser_profile
    CC=7  in:0  out:12  total:12
  urirun_connector_twin.prompt_plan._raw_steps_for_target
    CC=13  in:1  out:11  total:12
  urirun_connector_twin.core.step_feasibility
    CC=4  in:0  out:12  total:12
  urirun_connector_twin.core._prompt_result
    CC=5  in:1  out:11  total:12
  urirun_connector_twin.dispatch.uri_call
    CC=10  in:6  out:5  total:11
  urirun_connector_twin.prompt_plan.derive_task_target
    CC=2  in:5  out:6  total:11
  urirun_connector_twin.browser._selection
    CC=6  in:3  out:7  total:10
  urirun_connector_twin.mock.generate_mock
    CC=5  in:4  out:6  total:10
  urirun_connector_twin.prompt_plan._extract_text_to_type
    CC=5  in:1  out:8  total:9
  urirun_connector_twin.sandbox._parse_sections
    CC=2  in:1  out:7  total:8

MODULES:
  urirun_connector_twin.browser  [11 funcs]
    _cdp_cookies  CC=13  out:32
    _cdp_pages  CC=2  out:4
    _domain_key  CC=3  out:3
    _extract_chrome_info  CC=5  out:4
    _extract_flag  CC=3  out:3
    _is_browser  CC=3  out:3
    _port_open  CC=2  out:1
    _proc_cmdline  CC=2  out:4
    _selection  CC=6  out:7
    discover_browser_sessions  CC=15  out:17
  urirun_connector_twin.core  [17 funcs]
    _local_browser_profile  CC=1  out:3
    _prompt_result  CC=5  out:11
    _run_compose  CC=4  out:2
    _safe_import  CC=3  out:2
    _target_of  CC=2  out:2
    browser_profile  CC=7  out:12
    browser_sessions  CC=3  out:6
    constraints_from_profile  CC=4  out:5
    environment_profile  CC=2  out:3
    flow_preflight  CC=9  out:14
  urirun_connector_twin.dispatch  [2 funcs]
    uri_call  CC=10  out:5
    value_of  CC=4  out:4
  urirun_connector_twin.environment  [7 funcs]
    _constraints_from_profile_local  CC=3  out:2
    _constraints_via_uri  CC=3  out:4
    _host_os_info  CC=1  out:7
    _kvm_query  CC=4  out:3
    _probe_browser  CC=5  out:6
    _safe_import  CC=3  out:2
    probe  CC=11  out:17
  urirun_connector_twin.mock  [4 funcs]
    _compose_yaml  CC=3  out:3
    _detect_service  CC=3  out:2
    _resolve_service  CC=5  out:2
    generate_mock  CC=5  out:6
  urirun_connector_twin.planner  [7 funcs]
    _is_infeasible  CC=5  out:3
    _route_suffix  CC=2  out:4
    _step_reversible  CC=3  out:2
    _step_surface  CC=7  out:3
    annotate_steps  CC=8  out:13
    build_imperative_plan  CC=8  out:14
    extract_steps_from_flow  CC=4  out:4
  urirun_connector_twin.prompt_plan  [20 funcs]
    _bind_node  CC=1  out:1
    _browser_fill_and_submit_steps  CC=1  out:1
    _browser_open_steps  CC=1  out:0
    _classify_task_type  CC=6  out:2
    _extract_domain  CC=5  out:4
    _extract_query  CC=3  out:5
    _extract_text_to_type  CC=5  out:8
    _extract_url  CC=2  out:2
    _fallback_describe_steps  CC=1  out:0
    _guess_service_name  CC=2  out:3
  urirun_connector_twin.sandbox  [8 funcs]
    _docker_available  CC=1  out:1
    _docker_probe  CC=1  out:5
    _parse_sections  CC=2  out:7
    _run  CC=4  out:2
    _simulated_probe  CC=1  out:12
    _verdict  CC=4  out:0
    probe_reversibility  CC=2  out:4
    scenario_for_uri  CC=6  out:3

EDGES:
  urirun_connector_twin.sandbox._docker_probe → urirun_connector_twin.sandbox._run
  urirun_connector_twin.sandbox._docker_probe → urirun_connector_twin.sandbox._parse_sections
  urirun_connector_twin.sandbox._docker_probe → urirun_connector_twin.sandbox._verdict
  urirun_connector_twin.sandbox._simulated_probe → urirun_connector_twin.sandbox._run
  urirun_connector_twin.sandbox.probe_reversibility → urirun_connector_twin.sandbox._docker_available
  urirun_connector_twin.sandbox.probe_reversibility → urirun_connector_twin.sandbox._docker_probe
  urirun_connector_twin.sandbox.probe_reversibility → urirun_connector_twin.sandbox._simulated_probe
  urirun_connector_twin.mock._resolve_service → urirun_connector_twin.mock._detect_service
  urirun_connector_twin.mock.generate_mock → urirun_connector_twin.mock._resolve_service
  urirun_connector_twin.mock.generate_mock → urirun_connector_twin.mock._compose_yaml
  urirun_connector_twin.browser._cdp_cookies → urirun_connector_twin.browser._cdp_pages
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._proc_cmdline
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._extract_flag
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._port_open
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._is_browser
  urirun_connector_twin.browser.discover_browser_sessions → urirun_connector_twin.browser._cdp_pages
  urirun_connector_twin.browser.select_session → urirun_connector_twin.browser._domain_key
  urirun_connector_twin.browser.select_session → urirun_connector_twin.browser._selection
  urirun_connector_twin.browser._extract_chrome_info → urirun_connector_twin.browser._extract_flag
  urirun_connector_twin.browser._extract_chrome_info → urirun_connector_twin.browser._is_browser
  urirun_connector_twin.planner._is_infeasible → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner._step_surface → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner._step_reversible → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._is_infeasible
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._step_reversible
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._step_surface
  urirun_connector_twin.planner.build_imperative_plan → urirun_connector_twin.planner.extract_steps_from_flow
  urirun_connector_twin.planner.build_imperative_plan → urirun_connector_twin.planner.annotate_steps
  urirun_connector_twin.core._local_browser_profile → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core._local_browser_profile → urirun_connector_twin.browser.select_session
  urirun_connector_twin.core._prompt_result → urirun_connector_twin.mock.generate_mock
  urirun_connector_twin.core.environment_profile → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.constraints_from_profile → urirun_connector_twin.core._safe_import
  urirun_connector_twin.core.browser_sessions → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core.browser_profile → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core.browser_profile → urirun_connector_twin.browser.select_session
  urirun_connector_twin.core.browser_profile → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.prompt_plan.plan_from_prompt
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.dispatch.uri_call
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.core._prompt_result
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.dispatch.value_of
  urirun_connector_twin.core.plan_from_prompt_route → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.plan_annotate → urirun_connector_twin.planner.build_imperative_plan
  urirun_connector_twin.core.plan_generate → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.plan_generate → urirun_connector_twin.planner.build_imperative_plan
  urirun_connector_twin.core.plan_generate → urirun_connector_twin.mock.generate_mock
  urirun_connector_twin.core.mock_create → urirun_connector_twin.environment.probe
  urirun_connector_twin.core.mock_create → urirun_connector_twin.planner.build_imperative_plan
  urirun_connector_twin.core.mock_create → urirun_connector_twin.mock.generate_mock
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 18f 3169L | python:10,yaml:4,shell:2,json:1,toml:1 | 2026-06-26
# generated in 0.00s
# CC̅=4.1 | critical:2/92 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    discover_browser_sessions CC=15 (limit:15)
  🟡 CC    select_session CC=15 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[23]:
  [1] Src [_extract_chrome_info]: _extract_chrome_info → _extract_flag
      PURITY: 100% pure
  [2] Src [select_best_session]: select_best_session
      PURITY: 100% pure
  [3] Src [environment_profile]: environment_profile → probe → _host_os_info
      PURITY: 100% pure
  [4] Src [constraints_from_profile]: constraints_from_profile → _safe_import
      PURITY: 100% pure
  [5] Src [browser_sessions]: browser_sessions → discover_browser_sessions → _proc_cmdline
      PURITY: 100% pure
  [6] Src [browser_profile]: browser_profile → discover_browser_sessions → _proc_cmdline
      PURITY: 100% pure
  [7] Src [plan_from_prompt_route]: plan_from_prompt_route → derive_task_target → _extract_domain → _extract_url
      PURITY: 100% pure
  [8] Src [plan_annotate]: plan_annotate → build_imperative_plan → extract_steps_from_flow
      PURITY: 100% pure
  [9] Src [plan_generate]: plan_generate → probe → _host_os_info
      PURITY: 100% pure
  [10] Src [mock_create]: mock_create → probe → _host_os_info
      PURITY: 100% pure
  [11] Src [mock_start_probe_stop]: mock_start_probe_stop → probe → _host_os_info
      PURITY: 100% pure
  [12] Src [step_feasibility]: step_feasibility → probe → _host_os_info
      PURITY: 100% pure
  [13] Src [sandbox_probe]: sandbox_probe → probe_reversibility → _docker_available
      PURITY: 100% pure
  [14] Src [flow_preflight]: flow_preflight → _target_of
      PURITY: 100% pure
  [15] Src [flow_goal_verify]: flow_goal_verify
      PURITY: 100% pure
  [16] Src [flow_rollback]: flow_rollback
      PURITY: 100% pure
  [17] Src [step_evaluate]: step_evaluate
      PURITY: 100% pure
  [18] Src [flow_execute]: flow_execute
      PURITY: 100% pure
  [19] Src [flow_diagnose]: flow_diagnose
      PURITY: 100% pure
  [20] Src [monitor_event]: monitor_event
      PURITY: 100% pure
  [21] Src [bindings]: bindings
      PURITY: 100% pure
  [22] Src [manifest]: manifest
      PURITY: 100% pure
  [23] Src [main]: main
      PURITY: 100% pure

LAYERS:
  urirun_connector_twin/          CC̄=4.1    ←in:0  →out:0
  │ !! core                       573L  0C   28m  CC=13     ←0
  │ !! browser                    327L  0C   13m  CC=15     ←2
  │ prompt_plan                259L  0C   21m  CC=13     ←2
  │ sandbox                    162L  1C    8m  CC=6      ←1
  │ environment                161L  0C    8m  CC=11     ←1
  │ planner                    127L  0C    7m  CC=8      ←1
  │ mock                       114L  0C    4m  CC=5      ←1
  │ dispatch                    72L  0C    3m  CC=10     ←2
  │ session                     24L  0C    0m  CC=0.0    ←0
  │ __init__                     4L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! connector.manifest.json    616L  0C    0m  CC=0.0    ←0
  │ planfile.yaml              487L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ project.sh                  69L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              28L  0C    0m  CC=0.0    ←0
  │ tree.sh                      4L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    28L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 0f 0L | 2026-06-26

SUMMARY:
  files_scanned: 0
  total_lines:   0
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       3
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 92 func | 8f | 2026-06-26
# generated in 0.00s

NEXT[4] (ranked by impact):
  [1] !! SPLIT           urirun_connector_twin/core.py
      WHY: 573L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 7449

  [2] !  SPLIT-FUNC      discover_browser_sessions  CC=15  fan=13
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 195

  [3] !  SPLIT-FUNC      select_session  CC=15  fan=7
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 105

  [4] !! SPLIT           connector.manifest.json
      WHY: 616L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting connector.manifest.json may break 0 import paths
  ⚠ Splitting urirun_connector_twin/core.py may break 28 import paths

METRICS-TARGET:
  CC̄:          4.1 → ≤2.9
  max-CC:      15 → ≤7
  god-modules: 2 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=4.4 → now CC̄=4.1
```

## Intent

Digital Twin connector for urirun — environment probe, imperative plan generation, Docker mock fallback

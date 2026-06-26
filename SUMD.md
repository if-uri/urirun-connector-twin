# urirun-connector-twin

Digital Twin connector for urirun — environment probe, imperative plan generation, Docker mock fallback

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `urirun-connector-twin`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, project/(3 analysis files)

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

## Interfaces

### CLI Entry Points

- `urirun-connector-twin`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m urirun-connector-twin
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m urirun-connector-twin --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m urirun-connector-twin --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m urirun-connector-twin --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 18 assertions from pytest
ASSERT[18]{field, operator, expected}:
  len(env.ledger), ==, 2
  inverse_calls, ==, ["inverse-b"
  _extract_url("open https://linkedin.com/feed now"), ==, "https://linkedin.com/feed"
  _extract_domain("go to https://github.com/if-uri"), ==, "github.com"
  t.taskType, ==, "browser-open"
  t.url, ==, "https://github.com"
  sel.mode, ==, "attach"
  sel.port, ==, 9333
  sel.profileType, ==, "real"
  len(env.ledger), ==, 2
  inverse_calls, ==, ["inverse-b"
  _extract_url("open https://linkedin.com/feed now"), ==, "https://linkedin.com/feed"
  _extract_domain("go to https://github.com/if-uri"), ==, "github.com"
  t.taskType, ==, "browser-open"
  t.url, ==, "https://github.com"
  sel.mode, ==, "attach"
  sel.port, ==, 9333
  sel.profileType, ==, "real"
```

## Configuration

```yaml
project:
  name: urirun-connector-twin
  version: 0.1.0
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
urirun @ git+https://github.com/if-uri/urirun.git#subdirectory=adapters/python
```

## Deployment

```bash markpact:run
pip install urirun-connector-twin

# development install
pip install -e .[dev]
```

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# urirun-connector-twin | 18f 3990L | python:15,shell:2,less:1 | 2026-06-26
# stats: 253 func | 1 cls | 18 mod | CC̄=3.7 | critical:12 | cycles:0
# alerts[5]: CC derive_task_target=22; CC steps_from_prompt=16; CC discover_browser_sessions=15; CC select_session=15; CC _cdp_cookies=13
# hotspots[5]: _cdp_cookies fan=19; _cdp_ws_call fan=14; discover_browser_sessions fan=13; mock_start_probe_stop fan=13; steps_from_prompt fan=13
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[18]:
  app.doql.less,32
  project.sh,69
  tests/test_browser_session.py,271
  tests/test_dispatch.py,209
  tests/test_rollback_parity.py,250
  tests/test_session.py,233
  tests/test_twin_connector.py,943
  tree.sh,5
  urirun_connector_twin/__init__.py,5
  urirun_connector_twin/browser.py,279
  urirun_connector_twin/core.py,513
  urirun_connector_twin/dispatch.py,73
  urirun_connector_twin/environment.py,162
  urirun_connector_twin/mock.py,115
  urirun_connector_twin/planner.py,128
  urirun_connector_twin/prompt_plan.py,257
  urirun_connector_twin/sandbox.py,163
  urirun_connector_twin/session.py,283
D:
  tests/test_browser_session.py:
    e: test_derive_task_target_linkedin,test_derive_task_target_google,test_derive_task_target_unknown,test_derive_task_target_twitter,test_extract_chrome_info_with_port,test_extract_chrome_info_no_port,test_extract_chrome_info_not_chrome,test_extract_chrome_info_tmp_profile,_make_session,test_select_best_auth_confirmed,test_select_best_holds_target_fallback,test_select_best_needs_login_when_no_auth,test_select_best_no_chrome,test_select_best_no_auth_required,test_extract_url,test_extract_domain_from_url,test_extract_domain_from_keyword,test_extract_text_to_type_quoted,test_extract_text_to_type_after_verb,test_prompt_derive_social_post,test_prompt_derive_search,test_prompt_derive_screenshot,test_prompt_derive_browser_open,test_prompt_derive_unknown,test_steps_from_prompt_social_post,test_steps_from_prompt_screenshot,test_steps_from_prompt_search,test_steps_from_prompt_unknown_fallback,test_plan_from_prompt_structure,test_plan_from_prompt_social_post_metadata,test_browser_sessions_route_no_chrome,test_browser_profile_route_no_chrome,test_plan_from_prompt_route
    test_derive_task_target_linkedin()
    test_derive_task_target_google()
    test_derive_task_target_unknown()
    test_derive_task_target_twitter()
    test_extract_chrome_info_with_port()
    test_extract_chrome_info_no_port()
    test_extract_chrome_info_not_chrome()
    test_extract_chrome_info_tmp_profile()
    _make_session(port;user_data_dir;reachable;auth_confirmed;holds_target;auth_cookie)
    test_select_best_auth_confirmed()
    test_select_best_holds_target_fallback()
    test_select_best_needs_login_when_no_auth()
    test_select_best_no_chrome()
    test_select_best_no_auth_required()
    test_extract_url()
    test_extract_domain_from_url()
    test_extract_domain_from_keyword()
    test_extract_text_to_type_quoted()
    test_extract_text_to_type_after_verb()
    test_prompt_derive_social_post()
    test_prompt_derive_search()
    test_prompt_derive_screenshot()
    test_prompt_derive_browser_open()
    test_prompt_derive_unknown()
    test_steps_from_prompt_social_post()
    test_steps_from_prompt_screenshot()
    test_steps_from_prompt_search()
    test_steps_from_prompt_unknown_fallback()
    test_plan_from_prompt_structure()
    test_plan_from_prompt_social_post_metadata()
    test_browser_sessions_route_no_chrome(monkeypatch)
    test_browser_profile_route_no_chrome(monkeypatch)
    test_plan_from_prompt_route(monkeypatch)
  tests/test_dispatch.py:
    e: clean_transport,test_uri_call_fallback_triggers_on_no_mesh,test_uri_call_fallback_none_returns_none,test_value_of_extracts_value_key,test_value_of_extracts_nested_result_value,test_value_of_none_input,test_value_of_no_value_key,test_transport_is_called_first,test_transport_result_not_ok_falls_to_fallback,test_transport_exception_falls_to_fallback,test_set_transport_none_clears,test_plan_from_prompt_route_calls_environment_uri,test_plan_from_prompt_route_calls_browser_uri_when_domain,test_plan_from_prompt_route_fallback_when_no_transport,test_plan_from_prompt_route_calls_annotate_uri,test_plan_annotate_handler_returns_plan,test_all_three_from_prompt_steps_use_uri
    clean_transport()
    test_uri_call_fallback_triggers_on_no_mesh()
    test_uri_call_fallback_none_returns_none()
    test_value_of_extracts_value_key()
    test_value_of_extracts_nested_result_value()
    test_value_of_none_input()
    test_value_of_no_value_key()
    test_transport_is_called_first()
    test_transport_result_not_ok_falls_to_fallback()
    test_transport_exception_falls_to_fallback()
    test_set_transport_none_clears()
    test_plan_from_prompt_route_calls_environment_uri()
    test_plan_from_prompt_route_calls_browser_uri_when_domain()
    test_plan_from_prompt_route_fallback_when_no_transport()
    test_plan_from_prompt_route_calls_annotate_uri()
    test_plan_annotate_handler_returns_plan()
    test_all_three_from_prompt_steps_use_uri()
  tests/test_rollback_parity.py:
    e: _nav_step,_nav_result_with_inverse,test_envelope_ledger_filled_from_inverse,test_ledger_stays_empty_for_query_step,test_thin_driver_rollback_calls_inverse_lifo,test_thin_driver_rollback_returns_undone_list,test_two_reversible_steps_rolled_back_lifo,test_goal_failure_triggers_rollback,test_goal_none_result_is_treated_as_pass,test_flow_goal_verify_no_uri_is_pass,test_flow_goal_verify_no_goal_arg,test_flow_rollback_empty_ledger,test_flow_rollback_none_inverse_skipped
    _nav_step(sid)
    _nav_result_with_inverse(sid)
    test_envelope_ledger_filled_from_inverse()
    test_ledger_stays_empty_for_query_step()
    test_thin_driver_rollback_calls_inverse_lifo()
    test_thin_driver_rollback_returns_undone_list()
    test_two_reversible_steps_rolled_back_lifo()
    test_goal_failure_triggers_rollback()
    test_goal_none_result_is_treated_as_pass()
    test_flow_goal_verify_no_uri_is_pass()
    test_flow_goal_verify_no_goal_arg()
    test_flow_rollback_empty_ledger()
    test_flow_rollback_none_inverse_skipped()
  tests/test_session.py:
    e: test_derive_linkedin,test_derive_github,test_derive_google_no_auth,test_derive_unknown_prompt,test_derive_empty_prompt,test_extract_flag_debug_port,test_extract_flag_user_data_dir,test_extract_flag_missing_returns_none,test_is_browser_chrome,test_is_browser_chromium,test_is_browser_not_chrome,test_is_browser_empty,test_domain_key_linkedin,test_domain_key_github,test_domain_key_unknown,test_has_auth_cookie_linkedin_found,test_has_auth_cookie_linkedin_missing,test_has_auth_cookie_unknown_domain_any_match,_make_session,test_select_prefers_tab_on_domain_with_auth,test_select_real_profile_over_tmp,test_select_needs_login_when_no_reachable,test_select_no_needs_auth_picks_first_reachable,test_discover_returns_list,test_uri_call_returns_none_on_no_mesh,test_uri_call_fallback_none_returns_none,test_value_of_extracts_nested,test_value_of_none_input,test_constraints_from_profile_route_empty_matrix,test_constraints_from_profile_route_blocked_surface,test_probe_adds_infeasible_when_needs_login,test_browser_profile_handler_no_chrome
    test_derive_linkedin()
    test_derive_github()
    test_derive_google_no_auth()
    test_derive_unknown_prompt()
    test_derive_empty_prompt()
    test_extract_flag_debug_port()
    test_extract_flag_user_data_dir()
    test_extract_flag_missing_returns_none()
    test_is_browser_chrome()
    test_is_browser_chromium()
    test_is_browser_not_chrome()
    test_is_browser_empty()
    test_domain_key_linkedin()
    test_domain_key_github()
    test_domain_key_unknown()
    test_has_auth_cookie_linkedin_found()
    test_has_auth_cookie_linkedin_missing()
    test_has_auth_cookie_unknown_domain_any_match()
    _make_session(port;udd;reachable;pages;auth)
    test_select_prefers_tab_on_domain_with_auth()
    test_select_real_profile_over_tmp()
    test_select_needs_login_when_no_reachable()
    test_select_no_needs_auth_picks_first_reachable()
    test_discover_returns_list(monkeypatch)
    test_uri_call_returns_none_on_no_mesh()
    test_uri_call_fallback_none_returns_none()
    test_value_of_extracts_nested()
    test_value_of_none_input()
    test_constraints_from_profile_route_empty_matrix()
    test_constraints_from_profile_route_blocked_surface()
    test_probe_adds_infeasible_when_needs_login(monkeypatch)
    test_browser_profile_handler_no_chrome(monkeypatch)
  tests/test_twin_connector.py:
    e: test_probe_returns_host_info_without_node,test_probe_with_unknown_node_adds_warning,test_probe_merges_kvm_profile,test_constraints_from_profile_wayland_type,test_annotate_infeasible_os_type_step,test_annotate_cdp_fill_is_feasible,test_annotate_navigate_is_reversible,test_annotate_fill_is_irreversible,test_build_plan_counts_infeasible_steps,test_build_plan_no_infeasible_when_clean,test_detect_service_linkedin,test_detect_service_fallback,test_generate_mock_returns_reversible,test_generate_mock_compose_yaml,test_generate_mock_addresses_infeasible_uris,test_generate_mock_has_test_uri,test_connector_bindings_has_twin_routes,test_step_feasibility_handler_clean,test_mock_create_handler,test_sandbox_probe_simulated_reversible,test_sandbox_probe_simulated_irreversible,test_sandbox_probe_noop,test_scenario_for_uri_selects_builtin,test_sandbox_probe_handler_wires_up,test_step_evaluate_retry_on_transient,test_step_evaluate_heal_when_auto_applicable,test_step_evaluate_rollback_when_healed,test_step_evaluate_rollback_dry_run,test_flow_rollback_empty_ledger,test_flow_rollback_handler_in_bindings,test_flow_rollback_ledger_calls_inverses,test_abort_envelope_dispatches_rollback_ledger,test_evaluate_step_next_routes_through_dispatch_uri,test_evaluate_step_next_in_process_fallback,test_flow_preflight_no_cdp_steps_returns_empty,test_flow_preflight_extracts_cdp_targets,test_flow_preflight_dedups_same_host,test_flow_preflight_handles_ensure_failure_gracefully,test_execute_flow_auto_envelope_uses_thin_driver,test_execute_flow_without_dispatch_uses_orchestrator,_make_twin_memory,_make_dispatch_for_memory,test_build_thin_plan_injects_drift_and_remember_for_kvm_steps,test_build_thin_plan_kvm_always_gets_drift,test_build_thin_plan_no_kvm_no_drift,test_build_thin_plan_dry_run_no_drift,test_memory_dispatch_drift_sets_baseline_on_first_run,test_memory_dispatch_drift_detects_change,test_memory_dispatch_remember_updates_store,test_execute_flow_with_memory_injects_drift_steps,test_goal_verify_no_uri_is_noop,test_goal_verify_no_goal_at_all_is_noop,test_goal_verify_contains_passes,test_goal_verify_contains_fails,test_goal_verify_equals_passes,test_goal_verify_present_passes,test_goal_verify_transport_exception_returns_ok_false,test_goal_verify_dispatch_ok_false_fails_goal,test_mock_start_probe_stop_no_docker,test_mock_start_probe_stop_structure_has_mock_fields,test_thin_goal_verify_pass_returns_none,test_thin_goal_verify_fail_returns_rollback_dict,test_thin_goal_verify_registry_not_found_is_pass,test_thin_goal_verify_none_dispatch_result_is_pass
    test_probe_returns_host_info_without_node(monkeypatch)
    test_probe_with_unknown_node_adds_warning(monkeypatch)
    test_probe_merges_kvm_profile(monkeypatch)
    test_constraints_from_profile_wayland_type()
    test_annotate_infeasible_os_type_step()
    test_annotate_cdp_fill_is_feasible()
    test_annotate_navigate_is_reversible()
    test_annotate_fill_is_irreversible()
    test_build_plan_counts_infeasible_steps()
    test_build_plan_no_infeasible_when_clean()
    test_detect_service_linkedin()
    test_detect_service_fallback()
    test_generate_mock_returns_reversible()
    test_generate_mock_compose_yaml()
    test_generate_mock_addresses_infeasible_uris()
    test_generate_mock_has_test_uri()
    test_connector_bindings_has_twin_routes()
    test_step_feasibility_handler_clean(monkeypatch)
    test_mock_create_handler(monkeypatch)
    test_sandbox_probe_simulated_reversible(monkeypatch)
    test_sandbox_probe_simulated_irreversible(monkeypatch)
    test_sandbox_probe_noop(monkeypatch)
    test_scenario_for_uri_selects_builtin()
    test_sandbox_probe_handler_wires_up(monkeypatch)
    test_step_evaluate_retry_on_transient(monkeypatch)
    test_step_evaluate_heal_when_auto_applicable(monkeypatch)
    test_step_evaluate_rollback_when_healed(monkeypatch)
    test_step_evaluate_rollback_dry_run(monkeypatch)
    test_flow_rollback_empty_ledger()
    test_flow_rollback_handler_in_bindings()
    test_flow_rollback_ledger_calls_inverses()
    test_abort_envelope_dispatches_rollback_ledger(monkeypatch)
    test_evaluate_step_next_routes_through_dispatch_uri()
    test_evaluate_step_next_in_process_fallback(monkeypatch)
    test_flow_preflight_no_cdp_steps_returns_empty(monkeypatch)
    test_flow_preflight_extracts_cdp_targets(monkeypatch)
    test_flow_preflight_dedups_same_host(monkeypatch)
    test_flow_preflight_handles_ensure_failure_gracefully(monkeypatch)
    test_execute_flow_auto_envelope_uses_thin_driver()
    test_execute_flow_without_dispatch_uses_orchestrator()
    _make_twin_memory()
    _make_dispatch_for_memory(calls;profiles)
    test_build_thin_plan_injects_drift_and_remember_for_kvm_steps()
    test_build_thin_plan_kvm_always_gets_drift()
    test_build_thin_plan_no_kvm_no_drift()
    test_build_thin_plan_dry_run_no_drift()
    test_memory_dispatch_drift_sets_baseline_on_first_run(monkeypatch)
    test_memory_dispatch_drift_detects_change(monkeypatch)
    test_memory_dispatch_remember_updates_store(monkeypatch)
    test_execute_flow_with_memory_injects_drift_steps()
    test_goal_verify_no_uri_is_noop()
    test_goal_verify_no_goal_at_all_is_noop()
    test_goal_verify_contains_passes(monkeypatch)
    test_goal_verify_contains_fails(monkeypatch)
    test_goal_verify_equals_passes(monkeypatch)
    test_goal_verify_present_passes(monkeypatch)
    test_goal_verify_transport_exception_returns_ok_false(monkeypatch)
    test_goal_verify_dispatch_ok_false_fails_goal(monkeypatch)
    test_mock_start_probe_stop_no_docker(monkeypatch)
    test_mock_start_probe_stop_structure_has_mock_fields(monkeypatch)
    test_thin_goal_verify_pass_returns_none()
    test_thin_goal_verify_fail_returns_rollback_dict()
    test_thin_goal_verify_registry_not_found_is_pass()
    test_thin_goal_verify_none_dispatch_result_is_pass()
  urirun_connector_twin/__init__.py:
  urirun_connector_twin/browser.py:
    e: _proc_cmdline,_is_browser,_extract_flag,_cdp_pages,_cdp_cookies,_has_auth_cookie,_port_open,discover_browser_sessions,select_session,_domain_key,_selection
    _proc_cmdline(pid)
    _is_browser(args)
    _extract_flag(args;flag)
    _cdp_pages(port;timeout)
    _cdp_cookies(port;timeout)
    _has_auth_cookie(cookies;domain_key)
    _port_open(port;timeout)
    discover_browser_sessions(probe_cookies)
    select_session(sessions;domain;needs_auth)
    _domain_key(domain)
    _selection(mode;session;domain_key;rationale)
  urirun_connector_twin/core.py:
    e: _safe_import,_local_browser_profile,_apply_browser_sel,_prompt_result,environment_profile,constraints_from_profile,browser_sessions,browser_profile,plan_from_prompt_route,plan_annotate,plan_generate,mock_create,mock_start_probe_stop,_run_compose,_wait_for_http,step_feasibility,sandbox_probe,flow_preflight,_target_of,flow_goal_verify,flow_rollback,step_evaluate,monitor_event,bindings,manifest,main
    _safe_import(module)
    _local_browser_profile(domain;needs_auth)
    _apply_browser_sel(plan;browser_sel)
    _prompt_result(prompt;target;plan;env;include_mock)
    environment_profile(node;prompt)
    constraints_from_profile(actionMatrix)
    browser_sessions(probe_cookies)
    browser_profile(domain;prompt;probe_cookies)
    plan_from_prompt_route(prompt;node;include_mock;probe_browser)
    plan_annotate(flow;env;prompt)
    plan_generate(flow;prompt;node;include_mock)
    mock_create(prompt;flow;target)
    mock_start_probe_stop(prompt;flow;target;health_timeout)
    _run_compose(cmd)
    _wait_for_http(url)
    step_feasibility(uri;node;prompt)
    sandbox_probe(image;scan_cmd;forward_cmd;inverse_cmd;setup_cmd;uri)
    flow_preflight(steps;node)
    _target_of(uri)
    flow_goal_verify(goal;results)
    flow_rollback(ledger)
    step_evaluate(step;entry;routes;execute;attempt;max_retries;healed)
    monitor_event(node;stateSig;narration)
    bindings()
    manifest()
    main(argv)
  urirun_connector_twin/dispatch.py:
    e: set_transport,uri_call,value_of
    set_transport(fn)
    uri_call(uri;payload)
    value_of(result;key)
  urirun_connector_twin/environment.py:
    e: _safe_import,_kvm_query,_constraints_from_profile_local,_constraints_via_uri,_host_os_info,_docker_available,_probe_browser,probe
    _safe_import(module)
    _kvm_query(node;route)
    _constraints_from_profile_local(action_matrix)
    _constraints_via_uri(action_matrix)
    _host_os_info()
    _docker_available()
    _probe_browser(task)
    probe(node;prompt)
  urirun_connector_twin/mock.py:
    e: _detect_service,_resolve_service,_compose_yaml,generate_mock
    _detect_service(prompt;uris)
    _resolve_service(target;prompt;uris)
    _compose_yaml(service;spec)
    generate_mock(prompt;plan;target)
  urirun_connector_twin/planner.py:
    e: _route_suffix,_is_infeasible,_step_surface,_step_reversible,annotate_steps,extract_steps_from_flow,build_imperative_plan
    _route_suffix(uri)
    _is_infeasible(uri;constraints)
    _step_surface(uri;best_surface)
    _step_reversible(uri)
    annotate_steps(steps;env)
    extract_steps_from_flow(flow)
    build_imperative_plan(flow;env;prompt)
  urirun_connector_twin/prompt_plan.py:
    e: _extract_url,_extract_domain,_extract_text_to_type,_extract_query,_browser_open_steps,_browser_fill_and_submit_steps,_post_on_social_steps,_search_steps,_screenshot_steps,_file_write_steps,_service_start_steps,_service_stop_steps,_fallback_describe_steps,derive_task_target,steps_from_prompt,_guess_service_name,_bind_node,plan_from_prompt
    _extract_url(text)
    _extract_domain(text)
    _extract_text_to_type(text)
    _extract_query(text)
    _browser_open_steps(url)
    _browser_fill_and_submit_steps(url;field_text)
    _post_on_social_steps(domain;content)
    _search_steps(query)
    _screenshot_steps()
    _file_write_steps(path;content)
    _service_start_steps(service)
    _service_stop_steps(service)
    _fallback_describe_steps(prompt)
    derive_task_target(prompt)
    steps_from_prompt(prompt;node)
    _guess_service_name(prompt)
    _bind_node(step;node)
    plan_from_prompt(prompt;node)
  urirun_connector_twin/sandbox.py:
    e: scenario_for_uri,_docker_available,_run,_parse_sections,_verdict,_docker_probe,_simulated_probe,probe_reversibility,Scenario
    Scenario:  # One reversibility experiment.
    scenario_for_uri(uri)
    _docker_available()
    _run(cmd;timeout)
    _parse_sections(raw)
    _verdict(before;after;restored)
    _docker_probe(sc)
    _simulated_probe(sc)
    probe_reversibility(scenario)
  urirun_connector_twin/session.py:
    e: derive_task_target,_proc_cmdlines,_extract_chrome_info,discover_browser_sessions,_cdp_pages,_cdp_ws_call,_check_auth_cookies,probe_session,select_best_session
    derive_task_target(prompt)
    _proc_cmdlines()
    _extract_chrome_info(argv)
    discover_browser_sessions()
    _cdp_pages(port;timeout)
    _cdp_ws_call(ws_url;method;params;timeout)
    _check_auth_cookies(ws_url;domain)
    probe_session(session;domain)
    select_best_session(sessions;task)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('urirun-connector-twin', '0.1.0', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 32, 'less').
project_file('project.sh', 69, 'shell').
project_file('tests/test_browser_session.py', 271, 'python').
project_file('tests/test_dispatch.py', 209, 'python').
project_file('tests/test_rollback_parity.py', 250, 'python').
project_file('tests/test_session.py', 233, 'python').
project_file('tests/test_twin_connector.py', 943, 'python').
project_file('tree.sh', 5, 'shell').
project_file('urirun_connector_twin/__init__.py', 5, 'python').
project_file('urirun_connector_twin/browser.py', 279, 'python').
project_file('urirun_connector_twin/core.py', 513, 'python').
project_file('urirun_connector_twin/dispatch.py', 73, 'python').
project_file('urirun_connector_twin/environment.py', 162, 'python').
project_file('urirun_connector_twin/mock.py', 115, 'python').
project_file('urirun_connector_twin/planner.py', 128, 'python').
project_file('urirun_connector_twin/prompt_plan.py', 257, 'python').
project_file('urirun_connector_twin/sandbox.py', 163, 'python').
project_file('urirun_connector_twin/session.py', 283, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('tests/test_browser_session.py', 'test_derive_task_target_linkedin', 0, 3, 1).
python_function('tests/test_browser_session.py', 'test_derive_task_target_google', 0, 3, 1).
python_function('tests/test_browser_session.py', 'test_derive_task_target_unknown', 0, 3, 1).
python_function('tests/test_browser_session.py', 'test_derive_task_target_twitter', 0, 3, 1).
python_function('tests/test_browser_session.py', 'test_extract_chrome_info_with_port', 0, 4, 1).
python_function('tests/test_browser_session.py', 'test_extract_chrome_info_no_port', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_extract_chrome_info_not_chrome', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_extract_chrome_info_tmp_profile', 0, 3, 2).
python_function('tests/test_browser_session.py', '_make_session', 6, 1, 0).
python_function('tests/test_browser_session.py', 'test_select_best_auth_confirmed', 0, 4, 2).
python_function('tests/test_browser_session.py', 'test_select_best_holds_target_fallback', 0, 3, 2).
python_function('tests/test_browser_session.py', 'test_select_best_needs_login_when_no_auth', 0, 3, 3).
python_function('tests/test_browser_session.py', 'test_select_best_no_chrome', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_select_best_no_auth_required', 0, 3, 2).
python_function('tests/test_browser_session.py', 'test_extract_url', 0, 3, 1).
python_function('tests/test_browser_session.py', 'test_extract_domain_from_url', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_extract_domain_from_keyword', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_extract_text_to_type_quoted', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_extract_text_to_type_after_verb', 0, 2, 2).
python_function('tests/test_browser_session.py', 'test_prompt_derive_social_post', 0, 4, 1).
python_function('tests/test_browser_session.py', 'test_prompt_derive_search', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_prompt_derive_screenshot', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_prompt_derive_browser_open', 0, 3, 1).
python_function('tests/test_browser_session.py', 'test_prompt_derive_unknown', 0, 2, 1).
python_function('tests/test_browser_session.py', 'test_steps_from_prompt_social_post', 0, 6, 3).
python_function('tests/test_browser_session.py', 'test_steps_from_prompt_screenshot', 0, 3, 2).
python_function('tests/test_browser_session.py', 'test_steps_from_prompt_search', 0, 3, 2).
python_function('tests/test_browser_session.py', 'test_steps_from_prompt_unknown_fallback', 0, 3, 2).
python_function('tests/test_browser_session.py', 'test_plan_from_prompt_structure', 0, 4, 2).
python_function('tests/test_browser_session.py', 'test_plan_from_prompt_social_post_metadata', 0, 4, 1).
python_function('tests/test_browser_session.py', 'test_browser_sessions_route_no_chrome', 1, 3, 2).
python_function('tests/test_browser_session.py', 'test_browser_profile_route_no_chrome', 1, 3, 2).
python_function('tests/test_browser_session.py', 'test_plan_from_prompt_route', 1, 4, 2).
python_function('tests/test_dispatch.py', 'clean_transport', 0, 1, 1).
python_function('tests/test_dispatch.py', 'test_uri_call_fallback_triggers_on_no_mesh', 0, 2, 1).
python_function('tests/test_dispatch.py', 'test_uri_call_fallback_none_returns_none', 0, 2, 1).
python_function('tests/test_dispatch.py', 'test_value_of_extracts_value_key', 0, 2, 1).
python_function('tests/test_dispatch.py', 'test_value_of_extracts_nested_result_value', 0, 2, 1).
python_function('tests/test_dispatch.py', 'test_value_of_none_input', 0, 2, 1).
python_function('tests/test_dispatch.py', 'test_value_of_no_value_key', 0, 2, 1).
python_function('tests/test_dispatch.py', 'test_transport_is_called_first', 0, 3, 3).
python_function('tests/test_dispatch.py', 'test_transport_result_not_ok_falls_to_fallback', 0, 2, 2).
python_function('tests/test_dispatch.py', 'test_transport_exception_falls_to_fallback', 0, 3, 4).
python_function('tests/test_dispatch.py', 'test_set_transport_none_clears', 0, 3, 2).
python_function('tests/test_dispatch.py', 'test_plan_from_prompt_route_calls_environment_uri', 0, 5, 4).
python_function('tests/test_dispatch.py', 'test_plan_from_prompt_route_calls_browser_uri_when_domain', 0, 5, 4).
python_function('tests/test_dispatch.py', 'test_plan_from_prompt_route_fallback_when_no_transport', 0, 3, 1).
python_function('tests/test_dispatch.py', 'test_plan_from_prompt_route_calls_annotate_uri', 0, 5, 6).
python_function('tests/test_dispatch.py', 'test_plan_annotate_handler_returns_plan', 0, 5, 1).
python_function('tests/test_dispatch.py', 'test_all_three_from_prompt_steps_use_uri', 0, 3, 2).
python_function('tests/test_rollback_parity.py', '_nav_step', 1, 1, 0).
python_function('tests/test_rollback_parity.py', '_nav_result_with_inverse', 1, 1, 0).
python_function('tests/test_rollback_parity.py', 'test_envelope_ledger_filled_from_inverse', 0, 6, 6).
python_function('tests/test_rollback_parity.py', 'test_ledger_stays_empty_for_query_step', 0, 2, 2).
python_function('tests/test_rollback_parity.py', 'test_thin_driver_rollback_calls_inverse_lifo', 0, 4, 3).
python_function('tests/test_rollback_parity.py', 'test_thin_driver_rollback_returns_undone_list', 0, 3, 3).
python_function('tests/test_rollback_parity.py', 'test_two_reversible_steps_rolled_back_lifo', 0, 4, 4).
python_function('tests/test_rollback_parity.py', 'test_goal_failure_triggers_rollback', 0, 4, 3).
python_function('tests/test_rollback_parity.py', 'test_goal_none_result_is_treated_as_pass', 0, 2, 2).
python_function('tests/test_rollback_parity.py', 'test_flow_goal_verify_no_uri_is_pass', 0, 3, 2).
python_function('tests/test_rollback_parity.py', 'test_flow_goal_verify_no_goal_arg', 0, 2, 1).
python_function('tests/test_rollback_parity.py', 'test_flow_rollback_empty_ledger', 0, 3, 2).
python_function('tests/test_rollback_parity.py', 'test_flow_rollback_none_inverse_skipped', 0, 2, 1).
python_function('tests/test_session.py', 'test_derive_linkedin', 0, 3, 1).
python_function('tests/test_session.py', 'test_derive_github', 0, 3, 1).
python_function('tests/test_session.py', 'test_derive_google_no_auth', 0, 3, 1).
python_function('tests/test_session.py', 'test_derive_unknown_prompt', 0, 3, 1).
python_function('tests/test_session.py', 'test_derive_empty_prompt', 0, 2, 1).
python_function('tests/test_session.py', 'test_extract_flag_debug_port', 0, 2, 1).
python_function('tests/test_session.py', 'test_extract_flag_user_data_dir', 0, 2, 1).
python_function('tests/test_session.py', 'test_extract_flag_missing_returns_none', 0, 2, 1).
python_function('tests/test_session.py', 'test_is_browser_chrome', 0, 2, 1).
python_function('tests/test_session.py', 'test_is_browser_chromium', 0, 2, 1).
python_function('tests/test_session.py', 'test_is_browser_not_chrome', 0, 2, 1).
python_function('tests/test_session.py', 'test_is_browser_empty', 0, 2, 1).
python_function('tests/test_session.py', 'test_domain_key_linkedin', 0, 2, 1).
python_function('tests/test_session.py', 'test_domain_key_github', 0, 2, 1).
python_function('tests/test_session.py', 'test_domain_key_unknown', 0, 2, 1).
python_function('tests/test_session.py', 'test_has_auth_cookie_linkedin_found', 0, 2, 1).
python_function('tests/test_session.py', 'test_has_auth_cookie_linkedin_missing', 0, 2, 1).
python_function('tests/test_session.py', 'test_has_auth_cookie_unknown_domain_any_match', 0, 2, 1).
python_function('tests/test_session.py', '_make_session', 5, 3, 0).
python_function('tests/test_session.py', 'test_select_prefers_tab_on_domain_with_auth', 0, 4, 2).
python_function('tests/test_session.py', 'test_select_real_profile_over_tmp', 0, 3, 2).
python_function('tests/test_session.py', 'test_select_needs_login_when_no_reachable', 0, 3, 1).
python_function('tests/test_session.py', 'test_select_no_needs_auth_picks_first_reachable', 0, 2, 2).
python_function('tests/test_session.py', 'test_discover_returns_list', 1, 2, 3).
python_function('tests/test_session.py', 'test_uri_call_returns_none_on_no_mesh', 0, 2, 1).
python_function('tests/test_session.py', 'test_uri_call_fallback_none_returns_none', 0, 2, 1).
python_function('tests/test_session.py', 'test_value_of_extracts_nested', 0, 2, 1).
python_function('tests/test_session.py', 'test_value_of_none_input', 0, 2, 1).
python_function('tests/test_session.py', 'test_constraints_from_profile_route_empty_matrix', 0, 3, 2).
python_function('tests/test_session.py', 'test_constraints_from_profile_route_blocked_surface', 0, 3, 2).
python_function('tests/test_session.py', 'test_probe_adds_infeasible_when_needs_login', 1, 2, 2).
python_function('tests/test_session.py', 'test_browser_profile_handler_no_chrome', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_probe_returns_host_info_without_node', 1, 5, 2).
python_function('tests/test_twin_connector.py', 'test_probe_with_unknown_node_adds_warning', 1, 3, 3).
python_function('tests/test_twin_connector.py', 'test_probe_merges_kvm_profile', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_constraints_from_profile_wayland_type', 0, 2, 2).
python_function('tests/test_twin_connector.py', 'test_annotate_infeasible_os_type_step', 0, 4, 1).
python_function('tests/test_twin_connector.py', 'test_annotate_cdp_fill_is_feasible', 0, 2, 1).
python_function('tests/test_twin_connector.py', 'test_annotate_navigate_is_reversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_annotate_fill_is_irreversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_build_plan_counts_infeasible_steps', 0, 5, 1).
python_function('tests/test_twin_connector.py', 'test_build_plan_no_infeasible_when_clean', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_detect_service_linkedin', 0, 2, 1).
python_function('tests/test_twin_connector.py', 'test_detect_service_fallback', 0, 2, 1).
python_function('tests/test_twin_connector.py', 'test_generate_mock_returns_reversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_generate_mock_compose_yaml', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_generate_mock_addresses_infeasible_uris', 0, 2, 1).
python_function('tests/test_twin_connector.py', 'test_generate_mock_has_test_uri', 0, 2, 2).
python_function('tests/test_twin_connector.py', 'test_connector_bindings_has_twin_routes', 0, 5, 5).
python_function('tests/test_twin_connector.py', 'test_step_feasibility_handler_clean', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_mock_create_handler', 1, 4, 2).
python_function('tests/test_twin_connector.py', 'test_sandbox_probe_simulated_reversible', 1, 6, 3).
python_function('tests/test_twin_connector.py', 'test_sandbox_probe_simulated_irreversible', 1, 5, 3).
python_function('tests/test_twin_connector.py', 'test_sandbox_probe_noop', 1, 4, 3).
python_function('tests/test_twin_connector.py', 'test_scenario_for_uri_selects_builtin', 0, 4, 1).
python_function('tests/test_twin_connector.py', 'test_sandbox_probe_handler_wires_up', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_step_evaluate_retry_on_transient', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_step_evaluate_heal_when_auto_applicable', 1, 4, 2).
python_function('tests/test_twin_connector.py', 'test_step_evaluate_rollback_when_healed', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_step_evaluate_rollback_dry_run', 1, 2, 2).
python_function('tests/test_twin_connector.py', 'test_flow_rollback_empty_ledger', 0, 2, 2).
python_function('tests/test_twin_connector.py', 'test_flow_rollback_handler_in_bindings', 0, 5, 3).
python_function('tests/test_twin_connector.py', 'test_flow_rollback_ledger_calls_inverses', 0, 5, 2).
python_function('tests/test_twin_connector.py', 'test_abort_envelope_dispatches_rollback_ledger', 1, 8, 5).
python_function('tests/test_twin_connector.py', 'test_evaluate_step_next_routes_through_dispatch_uri', 0, 4, 3).
python_function('tests/test_twin_connector.py', 'test_evaluate_step_next_in_process_fallback', 1, 2, 2).
python_function('tests/test_twin_connector.py', 'test_flow_preflight_no_cdp_steps_returns_empty', 1, 4, 2).
python_function('tests/test_twin_connector.py', 'test_flow_preflight_extracts_cdp_targets', 1, 6, 6).
python_function('tests/test_twin_connector.py', 'test_flow_preflight_dedups_same_host', 1, 3, 4).
python_function('tests/test_twin_connector.py', 'test_flow_preflight_handles_ensure_failure_gracefully', 1, 6, 3).
python_function('tests/test_twin_connector.py', 'test_execute_flow_auto_envelope_uses_thin_driver', 0, 6, 4).
python_function('tests/test_twin_connector.py', 'test_execute_flow_without_dispatch_uses_orchestrator', 0, 3, 2).
python_function('tests/test_twin_connector.py', '_make_twin_memory', 0, 1, 2).
python_function('tests/test_twin_connector.py', '_make_dispatch_for_memory', 2, 2, 4).
python_function('tests/test_twin_connector.py', 'test_build_thin_plan_injects_drift_and_remember_for_kvm_steps', 0, 6, 3).
python_function('tests/test_twin_connector.py', 'test_build_thin_plan_kvm_always_gets_drift', 0, 5, 2).
python_function('tests/test_twin_connector.py', 'test_build_thin_plan_no_kvm_no_drift', 0, 4, 3).
python_function('tests/test_twin_connector.py', 'test_build_thin_plan_dry_run_no_drift', 0, 2, 2).
python_function('tests/test_twin_connector.py', 'test_memory_dispatch_drift_sets_baseline_on_first_run', 1, 4, 6).
python_function('tests/test_twin_connector.py', 'test_memory_dispatch_drift_detects_change', 1, 3, 6).
python_function('tests/test_twin_connector.py', 'test_memory_dispatch_remember_updates_store', 1, 4, 7).
python_function('tests/test_twin_connector.py', 'test_execute_flow_with_memory_injects_drift_steps', 0, 8, 8).
python_function('tests/test_twin_connector.py', 'test_goal_verify_no_uri_is_noop', 0, 4, 2).
python_function('tests/test_twin_connector.py', 'test_goal_verify_no_goal_at_all_is_noop', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_goal_verify_contains_passes', 1, 4, 3).
python_function('tests/test_twin_connector.py', 'test_goal_verify_contains_fails', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_goal_verify_equals_passes', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_goal_verify_present_passes', 1, 3, 2).
python_function('tests/test_twin_connector.py', 'test_goal_verify_transport_exception_returns_ok_false', 1, 4, 4).
python_function('tests/test_twin_connector.py', 'test_goal_verify_dispatch_ok_false_fails_goal', 1, 2, 2).
python_function('tests/test_twin_connector.py', 'test_mock_start_probe_stop_no_docker', 1, 7, 3).
python_function('tests/test_twin_connector.py', 'test_mock_start_probe_stop_structure_has_mock_fields', 1, 4, 4).
python_function('tests/test_twin_connector.py', 'test_thin_goal_verify_pass_returns_none', 0, 2, 2).
python_function('tests/test_twin_connector.py', 'test_thin_goal_verify_fail_returns_rollback_dict', 0, 4, 2).
python_function('tests/test_twin_connector.py', 'test_thin_goal_verify_registry_not_found_is_pass', 0, 2, 2).
python_function('tests/test_twin_connector.py', 'test_thin_goal_verify_none_dispatch_result_is_pass', 0, 2, 2).
python_function('urirun_connector_twin/browser.py', '_proc_cmdline', 1, 2, 4).
python_function('urirun_connector_twin/browser.py', '_is_browser', 1, 3, 3).
python_function('urirun_connector_twin/browser.py', '_extract_flag', 2, 3, 3).
python_function('urirun_connector_twin/browser.py', '_cdp_pages', 2, 2, 4).
python_function('urirun_connector_twin/browser.py', '_cdp_cookies', 2, 13, 19).
python_function('urirun_connector_twin/browser.py', '_has_auth_cookie', 2, 4, 2).
python_function('urirun_connector_twin/browser.py', '_port_open', 2, 2, 1).
python_function('urirun_connector_twin/browser.py', 'discover_browser_sessions', 1, 15, 13).
python_function('urirun_connector_twin/browser.py', 'select_session', 3, 15, 5).
python_function('urirun_connector_twin/browser.py', '_domain_key', 1, 3, 2).
python_function('urirun_connector_twin/browser.py', '_selection', 4, 6, 3).
python_function('urirun_connector_twin/core.py', '_safe_import', 1, 3, 2).
python_function('urirun_connector_twin/core.py', '_local_browser_profile', 2, 1, 3).
python_function('urirun_connector_twin/core.py', '_apply_browser_sel', 2, 3, 1).
python_function('urirun_connector_twin/core.py', '_prompt_result', 5, 5, 2).
python_function('urirun_connector_twin/core.py', 'environment_profile', 2, 2, 3).
python_function('urirun_connector_twin/core.py', 'constraints_from_profile', 1, 4, 4).
python_function('urirun_connector_twin/core.py', 'browser_sessions', 1, 3, 6).
python_function('urirun_connector_twin/core.py', 'browser_profile', 3, 7, 9).
python_function('urirun_connector_twin/core.py', 'plan_from_prompt_route', 4, 13, 11).
python_function('urirun_connector_twin/core.py', 'plan_annotate', 3, 1, 3).
python_function('urirun_connector_twin/core.py', 'plan_generate', 4, 4, 5).
python_function('urirun_connector_twin/core.py', 'mock_create', 3, 3, 6).
python_function('urirun_connector_twin/core.py', 'mock_start_probe_stop', 4, 7, 13).
python_function('urirun_connector_twin/core.py', '_run_compose', 1, 4, 2).
python_function('urirun_connector_twin/core.py', '_wait_for_http', 1, 5, 3).
python_function('urirun_connector_twin/core.py', 'step_feasibility', 3, 4, 5).
python_function('urirun_connector_twin/core.py', 'sandbox_probe', 6, 3, 4).
python_function('urirun_connector_twin/core.py', 'flow_preflight', 2, 9, 10).
python_function('urirun_connector_twin/core.py', '_target_of', 1, 2, 1).
python_function('urirun_connector_twin/core.py', 'flow_goal_verify', 2, 5, 6).
python_function('urirun_connector_twin/core.py', 'flow_rollback', 1, 8, 7).
python_function('urirun_connector_twin/core.py', 'step_evaluate', 7, 9, 4).
python_function('urirun_connector_twin/core.py', 'monitor_event', 3, 1, 2).
python_function('urirun_connector_twin/core.py', 'bindings', 0, 1, 1).
python_function('urirun_connector_twin/core.py', 'manifest', 0, 1, 2).
python_function('urirun_connector_twin/core.py', 'main', 1, 1, 2).
python_function('urirun_connector_twin/dispatch.py', 'set_transport', 1, 1, 0).
python_function('urirun_connector_twin/dispatch.py', 'uri_call', 2, 10, 4).
python_function('urirun_connector_twin/dispatch.py', 'value_of', 2, 4, 2).
python_function('urirun_connector_twin/environment.py', '_safe_import', 1, 3, 2).
python_function('urirun_connector_twin/environment.py', '_kvm_query', 2, 4, 3).
python_function('urirun_connector_twin/environment.py', '_constraints_from_profile_local', 1, 3, 2).
python_function('urirun_connector_twin/environment.py', '_constraints_via_uri', 1, 3, 4).
python_function('urirun_connector_twin/environment.py', '_host_os_info', 0, 1, 5).
python_function('urirun_connector_twin/environment.py', '_docker_available', 0, 2, 1).
python_function('urirun_connector_twin/environment.py', '_probe_browser', 1, 5, 4).
python_function('urirun_connector_twin/environment.py', 'probe', 2, 11, 8).
python_function('urirun_connector_twin/mock.py', '_detect_service', 2, 3, 2).
python_function('urirun_connector_twin/mock.py', '_resolve_service', 3, 5, 2).
python_function('urirun_connector_twin/mock.py', '_compose_yaml', 2, 3, 3).
python_function('urirun_connector_twin/mock.py', 'generate_mock', 3, 5, 3).
python_function('urirun_connector_twin/planner.py', '_route_suffix', 1, 2, 4).
python_function('urirun_connector_twin/planner.py', '_is_infeasible', 2, 5, 2).
python_function('urirun_connector_twin/planner.py', '_step_surface', 2, 7, 2).
python_function('urirun_connector_twin/planner.py', '_step_reversible', 1, 3, 2).
python_function('urirun_connector_twin/planner.py', 'annotate_steps', 2, 8, 7).
python_function('urirun_connector_twin/planner.py', 'extract_steps_from_flow', 1, 4, 1).
python_function('urirun_connector_twin/planner.py', 'build_imperative_plan', 3, 8, 4).
python_function('urirun_connector_twin/prompt_plan.py', '_extract_url', 1, 2, 2).
python_function('urirun_connector_twin/prompt_plan.py', '_extract_domain', 1, 5, 4).
python_function('urirun_connector_twin/prompt_plan.py', '_extract_text_to_type', 1, 5, 7).
python_function('urirun_connector_twin/prompt_plan.py', '_extract_query', 1, 3, 4).
python_function('urirun_connector_twin/prompt_plan.py', '_browser_open_steps', 1, 1, 0).
python_function('urirun_connector_twin/prompt_plan.py', '_browser_fill_and_submit_steps', 2, 1, 1).
python_function('urirun_connector_twin/prompt_plan.py', '_post_on_social_steps', 2, 2, 0).
python_function('urirun_connector_twin/prompt_plan.py', '_search_steps', 1, 1, 1).
python_function('urirun_connector_twin/prompt_plan.py', '_screenshot_steps', 0, 1, 0).
python_function('urirun_connector_twin/prompt_plan.py', '_file_write_steps', 2, 1, 0).
python_function('urirun_connector_twin/prompt_plan.py', '_service_start_steps', 1, 1, 0).
python_function('urirun_connector_twin/prompt_plan.py', '_service_stop_steps', 1, 1, 0).
python_function('urirun_connector_twin/prompt_plan.py', '_fallback_describe_steps', 1, 1, 0).
python_function('urirun_connector_twin/prompt_plan.py', 'derive_task_target', 1, 22, 5).
python_function('urirun_connector_twin/prompt_plan.py', 'steps_from_prompt', 2, 16, 13).
python_function('urirun_connector_twin/prompt_plan.py', '_guess_service_name', 1, 2, 3).
python_function('urirun_connector_twin/prompt_plan.py', '_bind_node', 2, 1, 1).
python_function('urirun_connector_twin/prompt_plan.py', 'plan_from_prompt', 2, 1, 3).
python_function('urirun_connector_twin/sandbox.py', 'scenario_for_uri', 1, 6, 3).
python_function('urirun_connector_twin/sandbox.py', '_docker_available', 0, 1, 1).
python_function('urirun_connector_twin/sandbox.py', '_run', 2, 4, 2).
python_function('urirun_connector_twin/sandbox.py', '_parse_sections', 1, 2, 3).
python_function('urirun_connector_twin/sandbox.py', '_verdict', 3, 4, 0).
python_function('urirun_connector_twin/sandbox.py', '_docker_probe', 1, 1, 5).
python_function('urirun_connector_twin/sandbox.py', '_simulated_probe', 1, 1, 7).
python_function('urirun_connector_twin/sandbox.py', 'probe_reversibility', 1, 2, 4).
python_function('urirun_connector_twin/session.py', 'derive_task_target', 1, 3, 2).
python_function('urirun_connector_twin/session.py', '_proc_cmdlines', 0, 7, 5).
python_function('urirun_connector_twin/session.py', '_extract_chrome_info', 1, 9, 5).
python_function('urirun_connector_twin/session.py', 'discover_browser_sessions', 0, 4, 5).
python_function('urirun_connector_twin/session.py', '_cdp_pages', 2, 2, 3).
python_function('urirun_connector_twin/session.py', '_cdp_ws_call', 4, 11, 14).
python_function('urirun_connector_twin/session.py', '_check_auth_cookies', 2, 10, 3).
python_function('urirun_connector_twin/session.py', 'probe_session', 2, 12, 4).
python_function('urirun_connector_twin/session.py', 'select_best_session', 2, 12, 1).

% ── Python Classes ───────────────────────────────────────
python_class('urirun_connector_twin/sandbox.py', 'Scenario').

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
```

## Call Graph

*77 nodes · 91 edges · 9 modules · CC̄=4.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_cdp_cookies` *(in urirun_connector_twin.browser)* | 13 ⚠ | 1 | 32 | **33** |
| `probe` *(in urirun_connector_twin.environment)* | 11 ⚠ | 7 | 17 | **24** |
| `_cdp_ws_call` *(in urirun_connector_twin.session)* | 11 ⚠ | 1 | 23 | **24** |
| `discover_browser_sessions` *(in urirun_connector_twin.browser)* | 15 ⚠ | 4 | 17 | **21** |
| `build_imperative_plan` *(in urirun_connector_twin.planner)* | 8 | 6 | 14 | **20** |
| `plan_from_prompt_route` *(in urirun_connector_twin.core)* | 13 ⚠ | 0 | 18 | **18** |
| `mock_start_probe_stop` *(in urirun_connector_twin.core)* | 7 | 0 | 16 | **16** |
| `steps_from_prompt` *(in urirun_connector_twin.prompt_plan)* | 16 ⚠ | 1 | 14 | **15** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/if-uri/urirun-connector-twin
# generated in 0.03s
# nodes: 77 | edges: 91 | modules: 9
# CC̄=4.6

HUBS[20]:
  urirun_connector_twin.browser._cdp_cookies
    CC=13  in:1  out:32  total:33
  urirun_connector_twin.environment.probe
    CC=11  in:7  out:17  total:24
  urirun_connector_twin.session._cdp_ws_call
    CC=11  in:1  out:23  total:24
  urirun_connector_twin.browser.discover_browser_sessions
    CC=15  in:4  out:17  total:21
  urirun_connector_twin.planner.build_imperative_plan
    CC=8  in:6  out:14  total:20
  urirun_connector_twin.core.plan_from_prompt_route
    CC=13  in:0  out:18  total:18
  urirun_connector_twin.core.mock_start_probe_stop
    CC=7  in:0  out:16  total:16
  urirun_connector_twin.prompt_plan.steps_from_prompt
    CC=16  in:1  out:14  total:15
  urirun_connector_twin.planner.annotate_steps
    CC=8  in:2  out:13  total:15
  urirun_connector_twin.core.flow_preflight
    CC=9  in:0  out:14  total:14
  urirun_connector_twin.prompt_plan.derive_task_target
    CC=22  in:2  out:12  total:14
  urirun_connector_twin.browser.select_session
    CC=15  in:3  out:11  total:14
  urirun_connector_twin.sandbox._simulated_probe
    CC=1  in:1  out:12  total:13
  urirun_connector_twin.core._prompt_result
    CC=5  in:1  out:11  total:12
  urirun_connector_twin.core.browser_profile
    CC=7  in:0  out:12  total:12
  urirun_connector_twin.core.step_feasibility
    CC=4  in:0  out:12  total:12
  urirun_connector_twin.dispatch.uri_call
    CC=10  in:6  out:5  total:11
  urirun_connector_twin.browser._selection
    CC=6  in:3  out:7  total:10
  urirun_connector_twin.mock.generate_mock
    CC=5  in:4  out:6  total:10
  urirun_connector_twin.session.probe_session
    CC=12  in:0  out:9  total:9

MODULES:
  urirun_connector_twin.browser  [10 funcs]
    _cdp_cookies  CC=13  out:32
    _cdp_pages  CC=2  out:4
    _domain_key  CC=3  out:3
    _extract_flag  CC=3  out:3
    _is_browser  CC=3  out:3
    _port_open  CC=2  out:1
    _proc_cmdline  CC=2  out:4
    _selection  CC=6  out:7
    discover_browser_sessions  CC=15  out:17
    select_session  CC=15  out:11
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
  urirun_connector_twin.prompt_plan  [14 funcs]
    _bind_node  CC=1  out:1
    _browser_fill_and_submit_steps  CC=1  out:1
    _browser_open_steps  CC=1  out:0
    _extract_domain  CC=5  out:4
    _extract_query  CC=3  out:5
    _extract_text_to_type  CC=5  out:8
    _extract_url  CC=2  out:2
    _guess_service_name  CC=2  out:3
    _post_on_social_steps  CC=2  out:0
    _screenshot_steps  CC=1  out:0
  urirun_connector_twin.sandbox  [8 funcs]
    _docker_available  CC=1  out:1
    _docker_probe  CC=1  out:5
    _parse_sections  CC=2  out:7
    _run  CC=4  out:2
    _simulated_probe  CC=1  out:12
    _verdict  CC=4  out:0
    probe_reversibility  CC=2  out:4
    scenario_for_uri  CC=6  out:3
  urirun_connector_twin.session  [8 funcs]
    _cdp_pages  CC=2  out:3
    _cdp_ws_call  CC=11  out:23
    _check_auth_cookies  CC=10  out:7
    _extract_chrome_info  CC=9  out:8
    _proc_cmdlines  CC=7  out:5
    derive_task_target  CC=3  out:2
    discover_browser_sessions  CC=4  out:5
    probe_session  CC=12  out:9

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
  urirun_connector_twin.planner._is_infeasible → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner._step_surface → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner._step_reversible → urirun_connector_twin.planner._route_suffix
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._is_infeasible
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._step_reversible
  urirun_connector_twin.planner.annotate_steps → urirun_connector_twin.planner._step_surface
  urirun_connector_twin.planner.build_imperative_plan → urirun_connector_twin.planner.extract_steps_from_flow
  urirun_connector_twin.planner.build_imperative_plan → urirun_connector_twin.planner.annotate_steps
  urirun_connector_twin.session.discover_browser_sessions → urirun_connector_twin.session._proc_cmdlines
  urirun_connector_twin.session.discover_browser_sessions → urirun_connector_twin.session._extract_chrome_info
  urirun_connector_twin.session._check_auth_cookies → urirun_connector_twin.session._cdp_ws_call
  urirun_connector_twin.session.probe_session → urirun_connector_twin.session._cdp_pages
  urirun_connector_twin.session.probe_session → urirun_connector_twin.session._check_auth_cookies
  urirun_connector_twin.prompt_plan._extract_domain → urirun_connector_twin.prompt_plan._extract_url
  urirun_connector_twin.prompt_plan._browser_fill_and_submit_steps → urirun_connector_twin.prompt_plan._browser_open_steps
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._extract_domain
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._extract_url
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._extract_text_to_type
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._post_on_social_steps
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._bind_node
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._search_steps
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._extract_query
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._browser_fill_and_submit_steps
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._browser_open_steps
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._screenshot_steps
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._guess_service_name
  urirun_connector_twin.prompt_plan.plan_from_prompt → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.prompt_plan.plan_from_prompt → urirun_connector_twin.prompt_plan.steps_from_prompt
  urirun_connector_twin.core._local_browser_profile → urirun_connector_twin.browser.discover_browser_sessions
  urirun_connector_twin.core._local_browser_profile → urirun_connector_twin.browser.select_session
  urirun_connector_twin.core._prompt_result → urirun_connector_twin.mock.generate_mock
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**
- assert `inverse_calls == ["inverse-b"`
- assert `inverse_calls == ["inverse-b"`

## Intent

Digital Twin connector for urirun — environment probe, imperative plan generation, Docker mock fallback

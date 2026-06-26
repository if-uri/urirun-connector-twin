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
# urirun-connector-twin | 21f 4942L | python:18,shell:2,less:1 | 2026-06-26
# stats: 289 func | 9 cls | 21 mod | CC̄=3.7 | critical:13 | cycles:0
# alerts[5]: CC test_append_twin_widget_emits_events_with_inverse=20; CC discover_browser_sessions=15; CC select_session=15; CC _cdp_cookies=13; CC plan_from_prompt_route=13
# hotspots[5]: _cdp_cookies fan=19; discover_browser_sessions fan=13; mock_start_probe_stop fan=13; plan_from_prompt_route fan=11; flow_preflight fan=10
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[21]:
  app.doql.less,32
  project.sh,69
  tests/test_browser_session.py,270
  tests/test_contract.py,40
  tests/test_dispatch.py,209
  tests/test_proof_cache.py,216
  tests/test_proof_routes.py,76
  tests/test_rollback_parity.py,380
  tests/test_session.py,233
  tests/test_twin_connector.py,1407
  tree.sh,5
  urirun_connector_twin/__init__.py,5
  urirun_connector_twin/browser.py,328
  urirun_connector_twin/core.py,615
  urirun_connector_twin/dispatch.py,73
  urirun_connector_twin/environment.py,162
  urirun_connector_twin/mock.py,115
  urirun_connector_twin/planner.py,128
  urirun_connector_twin/prompt_plan.py,260
  urirun_connector_twin/proof_cache.py,142
  urirun_connector_twin/sandbox.py,177
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
  tests/test_contract.py:
    e: TestTwinConnectorContract
    TestTwinConnectorContract: test_twin_routes_present(0)
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
  tests/test_proof_cache.py:
    e: TestScenarioSignature,TestProofKey,TestRouteHandlers,TestPreflightPaths,TestStoreContainsOnlyPositives
    TestScenarioSignature: test_signature_is_stable(0),test_signature_changes_on_inverse_change(0),test_signature_changes_on_forward_change(0)
    TestProofKey: setUp(0),test_proof_key_is_stable(0),test_proof_key_starts_with_pf(0),test_proof_key_changes_on_env_drift(0),test_proof_key_changes_on_scenario_change(0)
    TestRouteHandlers: setUp(0),test_proof_check_miss(0),test_proof_check_hit_after_record(0),test_proof_record_stores_positive_verdict(0),test_proof_record_does_not_store_negative_verdict(0),test_proof_check_missing_key_returns_error(0)
    TestPreflightPaths: setUp(0),_reversible_probe(0),_irreversible_probe(0),test_path1_new_env_miss_probe_proven_cached(0),test_path2_same_env_hit_sandbox_skipped(0),test_path3_env_drift_different_key_re_probed(0),test_path4_negative_block_not_cached(0)  # Structural proof of the four decision paths.
    TestStoreContainsOnlyPositives: test_store_shows_only_positive_entries(0)
  tests/test_proof_routes.py:
    e: TestProofRoutes
    TestProofRoutes: setUp(0),tearDown(0),test_check_miss_then_gate_probes_records_then_skip(0),test_drift_reprobes(0),test_irreversible_blocks_and_records_nothing(0),test_record_route_rejects_negative(0)
  tests/test_rollback_parity.py:
    e: _nav_step,_nav_result_with_inverse,test_envelope_ledger_filled_from_inverse,test_ledger_stays_empty_for_query_step,test_thin_driver_rollback_calls_inverse_lifo,test_thin_driver_rollback_returns_undone_list,test_two_reversible_steps_rolled_back_lifo,test_goal_failure_triggers_rollback,test_goal_none_result_is_treated_as_pass,test_flow_goal_verify_no_uri_is_pass,test_flow_goal_verify_no_goal_arg,test_flow_rollback_empty_ledger,test_flow_rollback_none_inverse_skipped,_undone_uris,_stuck_uri,test_three_path_rollback_convergence_success,test_three_path_rollback_convergence_stuck
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
    _undone_uris(undone)
    _stuck_uri(r)
    test_three_path_rollback_convergence_success()
    test_three_path_rollback_convergence_stuck()
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
    e: test_probe_returns_host_info_without_node,test_probe_with_unknown_node_adds_warning,test_probe_merges_kvm_profile,test_constraints_from_profile_wayland_type,test_annotate_infeasible_os_type_step,test_annotate_cdp_fill_is_feasible,test_annotate_navigate_is_reversible,test_annotate_fill_is_irreversible,test_build_plan_counts_infeasible_steps,test_build_plan_no_infeasible_when_clean,test_detect_service_linkedin,test_detect_service_fallback,test_generate_mock_returns_reversible,test_generate_mock_compose_yaml,test_generate_mock_addresses_infeasible_uris,test_generate_mock_has_test_uri,test_connector_bindings_has_twin_routes,test_step_feasibility_handler_clean,test_mock_create_handler,test_sandbox_probe_simulated_reversible,test_sandbox_probe_simulated_irreversible,test_sandbox_probe_noop,test_scenario_for_uri_selects_builtin,test_sandbox_probe_handler_wires_up,test_step_evaluate_retry_on_transient,test_step_evaluate_heal_when_auto_applicable,test_step_evaluate_rollback_when_healed,test_step_evaluate_rollback_dry_run,test_flow_rollback_empty_ledger,test_flow_rollback_handler_in_bindings,test_flow_rollback_ledger_calls_inverses,test_abort_envelope_dispatches_rollback_ledger,test_evaluate_step_next_routes_through_dispatch_uri,test_evaluate_step_next_in_process_fallback,test_flow_preflight_no_cdp_steps_returns_empty,test_flow_preflight_extracts_cdp_targets,test_flow_preflight_dedups_same_host,test_flow_preflight_handles_ensure_failure_gracefully,test_execute_flow_auto_envelope_uses_thin_driver,test_execute_flow_without_dispatch_uses_orchestrator,_make_twin_memory,_make_dispatch_for_memory,test_build_thin_plan_injects_drift_and_remember_for_kvm_steps,test_build_thin_plan_kvm_always_gets_drift,test_build_thin_plan_no_kvm_no_drift,test_build_thin_plan_dry_run_no_drift,test_memory_dispatch_drift_sets_baseline_on_first_run,test_memory_dispatch_drift_detects_change,test_memory_dispatch_remember_updates_store,test_execute_flow_with_memory_injects_drift_steps,test_goal_verify_no_uri_is_noop,test_goal_verify_no_goal_at_all_is_noop,test_goal_verify_contains_passes,test_goal_verify_contains_fails,test_goal_verify_equals_passes,test_goal_verify_present_passes,test_goal_verify_transport_exception_returns_ok_false,test_goal_verify_dispatch_ok_false_fails_goal,test_mock_start_probe_stop_no_docker,test_mock_start_probe_stop_structure_has_mock_fields,test_thin_goal_verify_pass_returns_none,test_thin_goal_verify_fail_returns_rollback_dict,test_thin_goal_verify_registry_not_found_is_pass,test_thin_goal_verify_none_dispatch_result_is_pass,test_flow_execute_handler_dry_run,test_flow_execute_handler_execute_mode,test_flow_execute_handler_step_failure_returns_ok_false,test_flow_execute_in_bindings,test_flow_diagnose_no_match_returns_found_false,test_flow_diagnose_service_stopped_matches,test_flow_diagnose_returns_remediation_list,test_flow_diagnose_in_bindings,test_step_inverse_query_is_reversible_no_inverse,test_step_inverse_navigate_is_reversible_with_back,test_step_inverse_session_ensure_reversible,test_step_inverse_click_is_irreversible,test_step_inverse_fill_is_irreversible,test_step_inverse_wait_is_reversible,test_step_inverse_unknown_command_is_irreversible,test_step_inverse_unknown_query_is_reversible,test_is_infra_step_skips_drift_and_preflight,test_is_infra_step_passes_real_steps,test_append_twin_widget_emits_events_with_inverse,test_convergence_navigate_inverse_matches_rollback_ledger,test_convergence_query_no_inverse_no_ledger,test_inverse_from_results_prefers_connector_over_static,test_inverse_from_results_handles_path_based_inverse,test_convergence_kvm_navigate_path_inverse_matches_ledger,test_degraded_step_shows_degraded_status_in_sse_event,test_non_degraded_query_step_shows_applied_status
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
    test_flow_execute_handler_dry_run(monkeypatch)
    test_flow_execute_handler_execute_mode(monkeypatch)
    test_flow_execute_handler_step_failure_returns_ok_false(monkeypatch)
    test_flow_execute_in_bindings()
    test_flow_diagnose_no_match_returns_found_false()
    test_flow_diagnose_service_stopped_matches()
    test_flow_diagnose_returns_remediation_list()
    test_flow_diagnose_in_bindings()
    test_step_inverse_query_is_reversible_no_inverse()
    test_step_inverse_navigate_is_reversible_with_back()
    test_step_inverse_session_ensure_reversible()
    test_step_inverse_click_is_irreversible()
    test_step_inverse_fill_is_irreversible()
    test_step_inverse_wait_is_reversible()
    test_step_inverse_unknown_command_is_irreversible()
    test_step_inverse_unknown_query_is_reversible()
    test_is_infra_step_skips_drift_and_preflight()
    test_is_infra_step_passes_real_steps()
    test_append_twin_widget_emits_events_with_inverse(monkeypatch)
    test_convergence_navigate_inverse_matches_rollback_ledger(monkeypatch)
    test_convergence_query_no_inverse_no_ledger(monkeypatch)
    test_inverse_from_results_prefers_connector_over_static(monkeypatch)
    test_inverse_from_results_handles_path_based_inverse(monkeypatch)
    test_convergence_kvm_navigate_path_inverse_matches_ledger(monkeypatch)
    test_degraded_step_shows_degraded_status_in_sse_event(monkeypatch)
    test_non_degraded_query_step_shows_applied_status(monkeypatch)
  urirun_connector_twin/__init__.py:
  urirun_connector_twin/browser.py:
    e: _proc_cmdline,_is_browser,_extract_flag,_cdp_pages,_cdp_cookies,_has_auth_cookie,_port_open,discover_browser_sessions,select_session,_extract_chrome_info,select_best_session,_domain_key,_selection
    _proc_cmdline(pid)
    _is_browser(args)
    _extract_flag(args;flag)
    _cdp_pages(port;timeout)
    _cdp_cookies(port;timeout)
    _has_auth_cookie(cookies;domain_key)
    _port_open(port;timeout)
    discover_browser_sessions(probe_cookies)
    select_session(sessions;domain;needs_auth)
    _extract_chrome_info(argv)
    select_best_session(sessions;task)
    _domain_key(domain)
    _selection(mode;session;domain_key;rationale)
  urirun_connector_twin/core.py:
    e: _safe_import,_local_browser_profile,_apply_browser_sel,_prompt_result,environment_profile,constraints_from_profile,browser_sessions,browser_profile,plan_from_prompt_route,plan_annotate,plan_generate,mock_create,mock_start_probe_stop,_run_compose,_wait_for_http,step_feasibility,sandbox_probe,_proof_store,proof_check_route,proof_record_route,proof_gate_route,flow_preflight,_target_of,flow_goal_verify,flow_rollback,step_evaluate,flow_execute,flow_diagnose,monitor_event,bindings,manifest,main
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
    _proof_store()
    proof_check_route(uri;env_fingerprint)
    proof_record_route(uri;env_fingerprint;verdict;scanned_before;scanned_after)
    proof_gate_route(uri;env_fingerprint)
    flow_preflight(steps;node)
    _target_of(uri)
    flow_goal_verify(goal;results)
    flow_rollback(ledger;mesh)
    step_evaluate(step;entry;routes;execute;attempt;max_retries;healed)
    flow_execute(flow;execute;max_retries;max_remediations;max_wall_clock)
    flow_diagnose(error;step;routes;environment;surface)
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
    e: _extract_url,_extract_domain,_extract_text_to_type,_extract_query,_browser_open_steps,_browser_fill_and_submit_steps,_post_on_social_steps,_search_steps,_screenshot_steps,_file_write_steps,_service_start_steps,_service_stop_steps,_fallback_describe_steps,_location_ok,_classify_task_type,derive_task_target,_raw_steps_for_target,steps_from_prompt,_guess_service_name,_bind_node,plan_from_prompt
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
    _location_ok(check;domain;url)
    _classify_task_type(low;domain;url)
    derive_task_target(prompt)
    _raw_steps_for_target(target;prompt)
    steps_from_prompt(prompt;node)
    _guess_service_name(prompt)
    _bind_node(step;node)
    plan_from_prompt(prompt;node)
  urirun_connector_twin/proof_cache.py:
    e: proof_key,proof_check,proof_record,preflight_step,DictProofStore
    DictProofStore: get(2)  # A plain dict that satisfies the store interface (get / __set
    proof_key(uri;scenario;env_fingerprint)
    proof_check(payload;store)
    proof_record(payload;store)
    preflight_step(uri;scenario;env_fingerprint;store;probe_fn;ts)
  urirun_connector_twin/sandbox.py:
    e: scenario_for_uri,_docker_available,_run,_parse_sections,_verdict,_docker_probe,_simulated_probe,probe_reversibility,Scenario
    Scenario: signature(0)  # One reversibility experiment.
    scenario_for_uri(uri)
    _docker_available()
    _run(cmd;timeout)
    _parse_sections(raw)
    _verdict(before;after;restored)
    _docker_probe(sc)
    _simulated_probe(sc)
    probe_reversibility(scenario)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('urirun-connector-twin', '0.1.0', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 32, 'less').
project_file('project.sh', 69, 'shell').
project_file('tests/test_browser_session.py', 270, 'python').
project_file('tests/test_contract.py', 40, 'python').
project_file('tests/test_dispatch.py', 209, 'python').
project_file('tests/test_proof_cache.py', 216, 'python').
project_file('tests/test_proof_routes.py', 76, 'python').
project_file('tests/test_rollback_parity.py', 380, 'python').
project_file('tests/test_session.py', 233, 'python').
project_file('tests/test_twin_connector.py', 1407, 'python').
project_file('tree.sh', 5, 'shell').
project_file('urirun_connector_twin/__init__.py', 5, 'python').
project_file('urirun_connector_twin/browser.py', 328, 'python').
project_file('urirun_connector_twin/core.py', 615, 'python').
project_file('urirun_connector_twin/dispatch.py', 73, 'python').
project_file('urirun_connector_twin/environment.py', 162, 'python').
project_file('urirun_connector_twin/mock.py', 115, 'python').
project_file('urirun_connector_twin/planner.py', 128, 'python').
project_file('urirun_connector_twin/prompt_plan.py', 260, 'python').
project_file('urirun_connector_twin/proof_cache.py', 142, 'python').
project_file('urirun_connector_twin/sandbox.py', 177, 'python').

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
python_function('tests/test_rollback_parity.py', '_undone_uris', 1, 6, 5).
python_function('tests/test_rollback_parity.py', '_stuck_uri', 1, 4, 4).
python_function('tests/test_rollback_parity.py', 'test_three_path_rollback_convergence_success', 0, 9, 8).
python_function('tests/test_rollback_parity.py', 'test_three_path_rollback_convergence_stuck', 0, 8, 9).
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
python_function('tests/test_twin_connector.py', 'test_flow_execute_handler_dry_run', 1, 5, 3).
python_function('tests/test_twin_connector.py', 'test_flow_execute_handler_execute_mode', 1, 5, 4).
python_function('tests/test_twin_connector.py', 'test_flow_execute_handler_step_failure_returns_ok_false', 1, 2, 2).
python_function('tests/test_twin_connector.py', 'test_flow_execute_in_bindings', 0, 2, 5).
python_function('tests/test_twin_connector.py', 'test_flow_diagnose_no_match_returns_found_false', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_flow_diagnose_service_stopped_matches', 0, 4, 2).
python_function('tests/test_twin_connector.py', 'test_flow_diagnose_returns_remediation_list', 0, 4, 2).
python_function('tests/test_twin_connector.py', 'test_flow_diagnose_in_bindings', 0, 2, 5).
python_function('tests/test_twin_connector.py', 'test_step_inverse_query_is_reversible_no_inverse', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_navigate_is_reversible_with_back', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_session_ensure_reversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_click_is_irreversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_fill_is_irreversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_wait_is_reversible', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_unknown_command_is_irreversible', 0, 2, 1).
python_function('tests/test_twin_connector.py', 'test_step_inverse_unknown_query_is_reversible', 0, 2, 1).
python_function('tests/test_twin_connector.py', 'test_is_infra_step_skips_drift_and_preflight', 0, 4, 1).
python_function('tests/test_twin_connector.py', 'test_is_infra_step_passes_real_steps', 0, 3, 1).
python_function('tests/test_twin_connector.py', 'test_append_twin_widget_emits_events_with_inverse', 1, 20, 9).
python_function('tests/test_twin_connector.py', 'test_convergence_navigate_inverse_matches_rollback_ledger', 1, 11, 8).
python_function('tests/test_twin_connector.py', 'test_convergence_query_no_inverse_no_ledger', 1, 9, 8).
python_function('tests/test_twin_connector.py', 'test_inverse_from_results_prefers_connector_over_static', 1, 6, 6).
python_function('tests/test_twin_connector.py', 'test_inverse_from_results_handles_path_based_inverse', 1, 2, 2).
python_function('tests/test_twin_connector.py', 'test_convergence_kvm_navigate_path_inverse_matches_ledger', 1, 9, 7).
python_function('tests/test_twin_connector.py', 'test_degraded_step_shows_degraded_status_in_sse_event', 1, 12, 8).
python_function('tests/test_twin_connector.py', 'test_non_degraded_query_step_shows_applied_status', 1, 6, 5).
python_function('urirun_connector_twin/browser.py', '_proc_cmdline', 1, 2, 4).
python_function('urirun_connector_twin/browser.py', '_is_browser', 1, 3, 3).
python_function('urirun_connector_twin/browser.py', '_extract_flag', 2, 3, 3).
python_function('urirun_connector_twin/browser.py', '_cdp_pages', 2, 2, 4).
python_function('urirun_connector_twin/browser.py', '_cdp_cookies', 2, 13, 19).
python_function('urirun_connector_twin/browser.py', '_has_auth_cookie', 2, 4, 2).
python_function('urirun_connector_twin/browser.py', '_port_open', 2, 2, 1).
python_function('urirun_connector_twin/browser.py', 'discover_browser_sessions', 1, 15, 13).
python_function('urirun_connector_twin/browser.py', 'select_session', 3, 15, 5).
python_function('urirun_connector_twin/browser.py', '_extract_chrome_info', 1, 5, 3).
python_function('urirun_connector_twin/browser.py', 'select_best_session', 2, 12, 3).
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
python_function('urirun_connector_twin/core.py', '_proof_store', 0, 1, 1).
python_function('urirun_connector_twin/core.py', 'proof_check_route', 2, 1, 5).
python_function('urirun_connector_twin/core.py', 'proof_record_route', 5, 1, 6).
python_function('urirun_connector_twin/core.py', 'proof_gate_route', 2, 1, 4).
python_function('urirun_connector_twin/core.py', 'flow_preflight', 2, 9, 10).
python_function('urirun_connector_twin/core.py', '_target_of', 1, 2, 1).
python_function('urirun_connector_twin/core.py', 'flow_goal_verify', 2, 5, 6).
python_function('urirun_connector_twin/core.py', 'flow_rollback', 2, 10, 8).
python_function('urirun_connector_twin/core.py', 'step_evaluate', 7, 9, 4).
python_function('urirun_connector_twin/core.py', 'flow_execute', 5, 3, 3).
python_function('urirun_connector_twin/core.py', 'flow_diagnose', 5, 4, 3).
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
python_function('urirun_connector_twin/prompt_plan.py', '_location_ok', 3, 4, 1).
python_function('urirun_connector_twin/prompt_plan.py', '_classify_task_type', 3, 6, 2).
python_function('urirun_connector_twin/prompt_plan.py', 'derive_task_target', 1, 2, 6).
python_function('urirun_connector_twin/prompt_plan.py', '_raw_steps_for_target', 2, 13, 10).
python_function('urirun_connector_twin/prompt_plan.py', 'steps_from_prompt', 2, 2, 3).
python_function('urirun_connector_twin/prompt_plan.py', '_guess_service_name', 1, 2, 3).
python_function('urirun_connector_twin/prompt_plan.py', '_bind_node', 2, 1, 1).
python_function('urirun_connector_twin/prompt_plan.py', 'plan_from_prompt', 2, 1, 3).
python_function('urirun_connector_twin/proof_cache.py', 'proof_key', 3, 1, 2).
python_function('urirun_connector_twin/proof_cache.py', 'proof_check', 2, 4, 1).
python_function('urirun_connector_twin/proof_cache.py', 'proof_record', 2, 10, 3).
python_function('urirun_connector_twin/proof_cache.py', 'preflight_step', 6, 9, 9).
python_function('urirun_connector_twin/sandbox.py', 'scenario_for_uri', 1, 6, 3).
python_function('urirun_connector_twin/sandbox.py', '_docker_available', 0, 1, 1).
python_function('urirun_connector_twin/sandbox.py', '_run', 2, 4, 2).
python_function('urirun_connector_twin/sandbox.py', '_parse_sections', 1, 2, 3).
python_function('urirun_connector_twin/sandbox.py', '_verdict', 3, 4, 0).
python_function('urirun_connector_twin/sandbox.py', '_docker_probe', 1, 1, 5).
python_function('urirun_connector_twin/sandbox.py', '_simulated_probe', 1, 1, 7).
python_function('urirun_connector_twin/sandbox.py', 'probe_reversibility', 1, 2, 4).

% ── Python Classes ───────────────────────────────────────
python_class('tests/test_contract.py', 'TestTwinConnectorContract').
python_method('TestTwinConnectorContract', 'test_twin_routes_present', 0, 5, 2).
python_class('tests/test_proof_cache.py', 'TestScenarioSignature').
python_method('TestScenarioSignature', 'test_signature_is_stable', 0, 1, 2).
python_method('TestScenarioSignature', 'test_signature_changes_on_inverse_change', 0, 1, 3).
python_method('TestScenarioSignature', 'test_signature_changes_on_forward_change', 0, 1, 3).
python_class('tests/test_proof_cache.py', 'TestProofKey').
python_method('TestProofKey', 'setUp', 0, 1, 0).
python_method('TestProofKey', 'test_proof_key_is_stable', 0, 1, 2).
python_method('TestProofKey', 'test_proof_key_starts_with_pf', 0, 1, 3).
python_method('TestProofKey', 'test_proof_key_changes_on_env_drift', 0, 1, 2).
python_method('TestProofKey', 'test_proof_key_changes_on_scenario_change', 0, 1, 3).
python_class('tests/test_proof_cache.py', 'TestRouteHandlers').
python_method('TestRouteHandlers', 'setUp', 0, 1, 2).
python_method('TestRouteHandlers', 'test_proof_check_miss', 0, 1, 3).
python_method('TestRouteHandlers', 'test_proof_check_hit_after_record', 0, 1, 5).
python_method('TestRouteHandlers', 'test_proof_record_stores_positive_verdict', 0, 1, 4).
python_method('TestRouteHandlers', 'test_proof_record_does_not_store_negative_verdict', 0, 1, 4).
python_method('TestRouteHandlers', 'test_proof_check_missing_key_returns_error', 0, 1, 2).
python_class('tests/test_proof_cache.py', 'TestPreflightPaths').
python_method('TestPreflightPaths', 'setUp', 0, 1, 1).
python_method('TestPreflightPaths', '_reversible_probe', 0, 1, 0).
python_method('TestPreflightPaths', '_irreversible_probe', 0, 1, 0).
python_method('TestPreflightPaths', 'test_path1_new_env_miss_probe_proven_cached', 0, 1, 4).
python_method('TestPreflightPaths', 'test_path2_same_env_hit_sandbox_skipped', 0, 1, 3).
python_method('TestPreflightPaths', 'test_path3_env_drift_different_key_re_probed', 0, 1, 5).
python_method('TestPreflightPaths', 'test_path4_negative_block_not_cached', 0, 1, 6).
python_class('tests/test_proof_cache.py', 'TestStoreContainsOnlyPositives').
python_method('TestStoreContainsOnlyPositives', 'test_store_shows_only_positive_entries', 0, 2, 7).
python_class('tests/test_proof_routes.py', 'TestProofRoutes').
python_method('TestProofRoutes', 'setUp', 0, 1, 3).
python_method('TestProofRoutes', 'tearDown', 0, 2, 2).
python_method('TestProofRoutes', 'test_check_miss_then_gate_probes_records_then_skip', 0, 1, 8).
python_method('TestProofRoutes', 'test_drift_reprobes', 0, 1, 3).
python_method('TestProofRoutes', 'test_irreversible_blocks_and_records_nothing', 0, 1, 5).
python_method('TestProofRoutes', 'test_record_route_rejects_negative', 0, 1, 3).
python_class('urirun_connector_twin/proof_cache.py', 'DictProofStore').
python_method('DictProofStore', 'get', 2, 1, 2).
python_class('urirun_connector_twin/sandbox.py', 'Scenario').
python_method('Scenario', 'signature', 0, 1, 4).

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

*84 nodes · 108 edges · 9 modules · CC̄=4.0*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_cdp_cookies` *(in urirun_connector_twin.browser)* | 13 ⚠ | 1 | 32 | **33** |
| `probe` *(in urirun_connector_twin.environment)* | 11 ⚠ | 7 | 17 | **24** |
| `discover_browser_sessions` *(in urirun_connector_twin.browser)* | 15 ⚠ | 4 | 17 | **21** |
| `build_imperative_plan` *(in urirun_connector_twin.planner)* | 8 | 6 | 14 | **20** |
| `plan_from_prompt_route` *(in urirun_connector_twin.core)* | 13 ⚠ | 0 | 18 | **18** |
| `preflight_step` *(in urirun_connector_twin.proof_cache)* | 9 | 1 | 15 | **16** |
| `mock_start_probe_stop` *(in urirun_connector_twin.core)* | 7 | 0 | 16 | **16** |
| `annotate_steps` *(in urirun_connector_twin.planner)* | 8 | 2 | 13 | **15** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/if-uri/urirun-connector-twin
# generated in 0.04s
# nodes: 84 | edges: 108 | modules: 9
# CC̄=4.0

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
  urirun_connector_twin.proof_cache.preflight_step
    CC=9  in:1  out:15  total:16
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
  urirun_connector_twin.core.step_feasibility
    CC=4  in:0  out:12  total:12
  urirun_connector_twin.core.browser_profile
    CC=7  in:0  out:12  total:12
  urirun_connector_twin.prompt_plan._raw_steps_for_target
    CC=13  in:1  out:11  total:12
  urirun_connector_twin.core._prompt_result
    CC=5  in:1  out:11  total:12
  urirun_connector_twin.proof_cache.proof_record
    CC=10  in:2  out:10  total:12
  urirun_connector_twin.prompt_plan.derive_task_target
    CC=2  in:5  out:6  total:11
  urirun_connector_twin.dispatch.uri_call
    CC=10  in:6  out:5  total:11
  urirun_connector_twin.browser._selection
    CC=6  in:3  out:7  total:10
  urirun_connector_twin.mock.generate_mock
    CC=5  in:4  out:6  total:10

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
  urirun_connector_twin.core  [21 funcs]
    _local_browser_profile  CC=1  out:3
    _prompt_result  CC=5  out:11
    _proof_store  CC=1  out:1
    _run_compose  CC=4  out:2
    _safe_import  CC=3  out:2
    _target_of  CC=2  out:2
    browser_profile  CC=7  out:12
    browser_sessions  CC=3  out:6
    constraints_from_profile  CC=4  out:5
    environment_profile  CC=2  out:3
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
  urirun_connector_twin.proof_cache  [4 funcs]
    preflight_step  CC=9  out:15
    proof_check  CC=4  out:4
    proof_key  CC=1  out:2
    proof_record  CC=10  out:10
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
  urirun_connector_twin.prompt_plan._extract_domain → urirun_connector_twin.prompt_plan._extract_url
  urirun_connector_twin.prompt_plan._browser_fill_and_submit_steps → urirun_connector_twin.prompt_plan._browser_open_steps
  urirun_connector_twin.prompt_plan._classify_task_type → urirun_connector_twin.prompt_plan._location_ok
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._extract_domain
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._extract_url
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._extract_text_to_type
  urirun_connector_twin.prompt_plan.derive_task_target → urirun_connector_twin.prompt_plan._classify_task_type
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._fallback_describe_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._post_on_social_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._search_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._browser_fill_and_submit_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._browser_open_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._screenshot_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._service_start_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._service_stop_steps
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._extract_query
  urirun_connector_twin.prompt_plan._raw_steps_for_target → urirun_connector_twin.prompt_plan._guess_service_name
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._bind_node
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan._raw_steps_for_target
  urirun_connector_twin.prompt_plan.steps_from_prompt → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.prompt_plan.plan_from_prompt → urirun_connector_twin.prompt_plan.derive_task_target
  urirun_connector_twin.prompt_plan.plan_from_prompt → urirun_connector_twin.prompt_plan.steps_from_prompt
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

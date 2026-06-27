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
project_file('tests/test_recall_routes.py', 140, 'python').
project_file('tests/test_rollback_parity.py', 380, 'python').
project_file('tests/test_session.py', 233, 'python').
project_file('tests/test_twin_connector.py', 1401, 'python').
project_file('tree.sh', 5, 'shell').
project_file('urirun_connector_twin/__init__.py', 5, 'python').
project_file('urirun_connector_twin/browser.py', 328, 'python').
project_file('urirun_connector_twin/core.py', 734, 'python').
project_file('urirun_connector_twin/dispatch.py', 73, 'python').
project_file('urirun_connector_twin/environment.py', 162, 'python').
project_file('urirun_connector_twin/mock.py', 115, 'python').
project_file('urirun_connector_twin/planner.py', 128, 'python').
project_file('urirun_connector_twin/prompt_plan.py', 262, 'python').
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
python_function('tests/test_recall_routes.py', '_ok_episode', 4, 1, 1).
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
python_function('tests/test_twin_connector.py', 'test_abort_envelope_dispatches_rollback_ledger', 1, 7, 3).
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
python_function('urirun_connector_twin/core.py', 'flow_recall', 5, 20, 11).
python_function('urirun_connector_twin/core.py', 'flow_episode_run', 5, 8, 6).
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
python_class('tests/test_recall_routes.py', 'TestFlowRecallRoute').
python_method('TestFlowRecallRoute', 'setUp', 0, 1, 3).
python_method('TestFlowRecallRoute', 'tearDown', 0, 2, 2).
python_method('TestFlowRecallRoute', '_mem', 0, 1, 1).
python_method('TestFlowRecallRoute', 'test_recall_by_episode_id_direct', 0, 2, 8).
python_method('TestFlowRecallRoute', 'test_recall_by_intent_and_env_fp', 0, 1, 8).
python_method('TestFlowRecallRoute', 'test_recall_intent_only_fallback_via_flow_store', 0, 2, 8).
python_method('TestFlowRecallRoute', 'test_recall_returns_not_found_for_unknown_prompt', 0, 1, 5).
python_method('TestFlowRecallRoute', 'test_recall_episode_id_missing_returns_not_found', 0, 1, 3).
python_class('tests/test_recall_routes.py', 'TestFlowEpisodeRun').
python_method('TestFlowEpisodeRun', 'setUp', 0, 1, 3).
python_method('TestFlowEpisodeRun', 'tearDown', 0, 2, 2).
python_method('TestFlowEpisodeRun', 'test_episode_run_missing_episode_returns_error', 0, 2, 4).
python_method('TestFlowEpisodeRun', 'test_episode_run_dispatches_stored_steps', 0, 1, 9).
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


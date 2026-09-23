# Raw CodeGraph callable relationships

**Not a verified runtime trace.** Dynamic dispatch can be missing or misresolved.
For example, worker.execute's runner.run is misresolved to Agent.run.
Use the main report for verified chains; graph.json retains all edge kinds and unresolved references.

## `aveli/__init__.py`

### `__getattr__` · line 6

No resolved outgoing call/type edge.

## `aveli/agent.py`

### `Agent` · line 12

No resolved outgoing call/type edge.

### `Agent::__init__` · line 13

- `aveli/agent.py:203 Agent::close (calls)`
- `aveli/browser.py:21 Browser (instantiates)`
- `aveli/browser.py:57 Browser::observe (calls)`

### `Agent::snapshot` · line 60

- `aveli/model.py:48 action_space (calls)`

### `Agent::command` · line 66

- `aveli/agent.py:60 Agent::snapshot (calls)`
- `aveli/agent.py:66 Agent::command (calls)`
- `aveli/browser.py:107 Browser::fresh (calls)`
- `aveli/browser.py:119 Browser::act (calls)`
- `aveli/browser.py:17 StalePage (instantiates)`
- `aveli/browser.py:57 Browser::observe (calls)`
- `aveli/model.py:152 field_context (calls)`
- `aveli/model.py:166 field_text (calls)`
- `aveli/model.py:81 choose (calls)`

### `Agent::command::before_mutation` · line 134

No resolved outgoing call/type edge.

### `Agent::proposed_action` · line 183

No resolved outgoing call/type edge.

### `Agent::run` · line 199

- `aveli/agent.py:66 Agent::command (calls)`

### `Agent::close` · line 203

- `aveli/agent.py:203 Agent::close (calls)`

### `Agent::__enter__` · line 206

No resolved outgoing call/type edge.

### `Agent::__exit__` · line 209

- `aveli/agent.py:203 Agent::close (calls)`

## `aveli/audit.py`

### `AuditSink` · line 13

No resolved outgoing call/type edge.

### `AuditSink::emit` · line 14

No resolved outgoing call/type edge.

### `NullAuditSink` · line 17

No resolved outgoing call/type edge.

### `NullAuditSink::emit` · line 18

No resolved outgoing call/type edge.

### `JsonlAuditSink` · line 22

No resolved outgoing call/type edge.

### `JsonlAuditSink::__init__` · line 25

No resolved outgoing call/type edge.

### `JsonlAuditSink::emit` · line 30

- `aveli/audit.py:46 _redact (calls)`

### `_redact` · line 46

- `aveli/audit.py:46 _redact (calls)`

## `aveli/browser.py`

### `StalePage` · line 17

No resolved outgoing call/type edge.

### `Browser` · line 21

No resolved outgoing call/type edge.

### `Browser::__init__` · line 22

- `aveli/browser.py:48 Browser::call (calls)`
- `aveli/browser.py:51 Browser::evaluate (calls)`

### `Browser::call` · line 48

No resolved outgoing call/type edge.

### `Browser::evaluate` · line 51

- `aveli/browser.py:17 StalePage (instantiates)`
- `aveli/browser.py:48 Browser::call (calls)`

### `Browser::observe` · line 57

- `aveli/browser.py:141 browser_operation (calls)`
- `aveli/browser.py:48 Browser::call (calls)`

### `Browser::fresh` · line 107

- `aveli/browser.py:51 Browser::evaluate (calls)`

### `Browser::act` · line 119

- `aveli/agent.py:134 Agent::command::before_mutation (calls)`
- `aveli/browser.py:107 Browser::fresh (calls)`
- `aveli/browser.py:141 browser_operation (calls)`
- `aveli/browser.py:17 StalePage (instantiates)`

### `Browser::close` · line 130

No resolved outgoing call/type edge.

### `fingerprint` · line 136

No resolved outgoing call/type edge.

### `browser_operation` · line 141

- `aveli/browser.py:136 fingerprint (calls)`
- `aveli/browser.py:145 browser_operation::call (calls)`
- `aveli/browser.py:148 browser_operation::evaluate (calls)`
- `aveli/browser.py:17 StalePage (instantiates)`

### `browser_operation::call` · line 145

No resolved outgoing call/type edge.

### `browser_operation::evaluate` · line 148

- `aveli/browser.py:145 browser_operation::call (calls)`
- `aveli/browser.py:17 StalePage (instantiates)`

## `aveli/config.py`

### `ConfigurationError` · line 10

No resolved outgoing call/type edge.

### `_required` · line 14

- `aveli/config.py:10 ConfigurationError (instantiates)`

### `_pinned_model` · line 21

- `aveli/config.py:10 ConfigurationError (instantiates)`
- `aveli/config.py:14 _required (calls)`

### `_absolute_directory` · line 28

- `aveli/config.py:10 ConfigurationError (instantiates)`
- `aveli/config.py:14 _required (calls)`

### `ProductionSettings` · line 36

No resolved outgoing call/type edge.

### `ProductionSettings::from_env` · line 50

- `aveli/config.py:10 ConfigurationError (instantiates)`
- `aveli/config.py:14 _required (calls)`
- `aveli/config.py:21 _pinned_model (calls)`
- `aveli/config.py:28 _absolute_directory (calls)`

### `ProductionSettings::provider_environment` · line 76

No resolved outgoing call/type edge.

## `aveli/demo.py`

### `load_environment` · line 23

No resolved outgoing call/type edge.

### `response_state` · line 32

- `aveli/agent.py:60 Agent::snapshot (calls)`

### `close_browser` · line 37

- `aveli/agent.py:203 Agent::close (calls)`

### `command` · line 44

- `aveli/agent.py:12 Agent (instantiates)`
- `aveli/agent.py:66 Agent::command (calls)`
- `aveli/demo.py:32 response_state (calls)`
- `aveli/demo.py:37 close_browser (calls)`

### `Handler` · line 70

No resolved outgoing call/type edge.

### `Handler::send` · line 71

No resolved outgoing call/type edge.

### `Handler::do_GET` · line 81

- `aveli/demo.py:32 response_state (calls)`
- `aveli/demo.py:71 Handler::send (calls)`

### `Handler::do_POST` · line 104

- `aveli/demo.py:44 command (calls)`
- `aveli/demo.py:71 Handler::send (calls)`

### `Handler::log_message` · line 127

No resolved outgoing call/type edge.

### `main` · line 131

- `aveli/demo.py:23 load_environment (calls)`

## `aveli/isolation.py`

### `require_active_isolation` · line 21

No resolved outgoing call/type edge.

### `ChromeConfig` · line 28

No resolved outgoing call/type edge.

### `ChromeConfig::from_env` · line 35

- `aveli/isolation.py:48 _chrome_candidates (calls)`

### `_chrome_candidates` · line 48

No resolved outgoing call/type edge.

### `_terminate_process_group` · line 62

- `tests/test_isolation.py:17 FakeProcess::poll (calls)`
- `tests/test_isolation.py:20 FakeProcess::terminate (calls)`
- `tests/test_isolation.py:24 FakeProcess::wait (calls)`
- `tests/test_isolation.py:29 FakeProcess::kill (calls)`

### `IsolatedChrome` · line 90

No resolved outgoing call/type edge.

### `IsolatedChrome::__init__` · line 104

No resolved outgoing call/type edge.

### `IsolatedChrome::__enter__` · line 132

- `aveli/isolation.py:132 IsolatedChrome::__enter__ (calls)`
- `aveli/isolation.py:191 IsolatedChrome::_wait_for_port (calls)`
- `aveli/isolation.py:206 IsolatedChrome::_set_environment (calls)`
- `aveli/isolation.py:232 IsolatedChrome::close (calls)`
- `aveli/network.py:77 AllowedHostProxy (instantiates)`

### `IsolatedChrome::_wait_for_port` · line 191

- `tests/test_isolation.py:17 FakeProcess::poll (calls)`

### `IsolatedChrome::_set_environment` · line 206

No resolved outgoing call/type edge.

### `IsolatedChrome::_stop_daemon` · line 220

No resolved outgoing call/type edge.

### `IsolatedChrome::close` · line 232

- `aveli/isolation.py:220 IsolatedChrome::_stop_daemon (calls)`
- `aveli/isolation.py:232 IsolatedChrome::close (calls)`

### `IsolatedChrome::__exit__` · line 272

- `aveli/isolation.py:232 IsolatedChrome::close (calls)`

## `aveli/job.py`

### `ActionClass` · line 11

No resolved outgoing call/type edge.

### `PolicyDisposition` · line 23

No resolved outgoing call/type edge.

### `JobStatus` · line 29

No resolved outgoing call/type edge.

### `_host` · line 40

No resolved outgoing call/type edge.

### `_strings` · line 58

No resolved outgoing call/type edge.

### `VerificationOutcome` · line 67

No resolved outgoing call/type edge.

### `VerificationSpec` · line 74

No resolved outgoing call/type edge.

### `VerificationSpec::from_dict` · line 81

- `aveli/job.py:40 _host (calls)`
- `aveli/job.py:58 _strings (calls)`

### `VerificationSpec::verify` · line 100

- `aveli/job.py:67 VerificationOutcome (instantiates)`

### `JobSpec` · line 125

No resolved outgoing call/type edge.

### `JobSpec::from_dict` · line 138

- `aveli/job.py:11 ActionClass (instantiates)`
- `aveli/job.py:40 _host (calls)`
- `aveli/job.py:58 _strings (calls)`
- `aveli/job.py:81 VerificationSpec::from_dict (calls)`

### `PolicyAssessment` · line 212

No resolved outgoing call/type edge.

### `ActionPolicy` · line 218

No resolved outgoing call/type edge.

### `ActionPolicy::__init__` · line 219

No resolved outgoing call/type edge.

### `ActionPolicy::check_page` · line 222

- `aveli/job.py:40 _host (calls)`

### `ActionPolicy::assess` · line 231

- `aveli/job.py:212 PolicyAssessment (instantiates)`
- `aveli/job.py:222 ActionPolicy::check_page (calls)`
- `aveli/job.py:251 classify_action (calls)`

### `classify_action` · line 251

No resolved outgoing call/type edge.

### `_digest` · line 272

No resolved outgoing call/type edge.

### `PreparedAction` · line 277

No resolved outgoing call/type edge.

### `PreparedAction::from_proposal` · line 291

- `aveli/job.py:251 classify_action (calls)`

### `PreparedAction::audit_fields` · line 305

- `aveli/job.py:272 _digest (calls)`

### `_public_url` · line 319

No resolved outgoing call/type edge.

### `JobResult` · line 334

No resolved outgoing call/type edge.

### `JobResult::__post_init__` · line 343

- `aveli/job.py:319 _public_url (calls)`

### `JobResult::to_dict` · line 346

No resolved outgoing call/type edge.

## `aveli/model.py`

### `post_json` · line 15

No resolved outgoing call/type edge.

### `validate_choice` · line 30

No resolved outgoing call/type edge.

### `action_space` · line 48

No resolved outgoing call/type edge.

### `choose` · line 81

- `aveli/model.py:15 post_json (calls)`
- `aveli/model.py:30 validate_choice (calls)`
- `aveli/model.py:48 action_space (calls)`

### `field_context` · line 152

No resolved outgoing call/type edge.

### `field_text` · line 166

- `aveli/model.py:15 post_json (calls)`

## `aveli/moli.py`

### `MoliConfig` · line 30

No resolved outgoing call/type edge.

### `MoliConfig::from_env` · line 38

No resolved outgoing call/type edge.

### `IsolatedMoli` · line 66

No resolved outgoing call/type edge.

### `IsolatedMoli::__init__` · line 69

No resolved outgoing call/type edge.

### `IsolatedMoli::__enter__` · line 90

- `aveli/moli.py:131 IsolatedMoli::_reserve_port (calls)`
- `aveli/moli.py:136 IsolatedMoli::_wait_until_ready (calls)`
- `aveli/moli.py:155 IsolatedMoli::_set_environment (calls)`
- `aveli/moli.py:183 IsolatedMoli::close (calls)`

### `IsolatedMoli::_reserve_port` · line 131

No resolved outgoing call/type edge.

### `IsolatedMoli::_wait_until_ready` · line 136

- `aveli/moli.py:147 IsolatedMoli::_ready (calls)`
- `tests/test_isolation.py:17 FakeProcess::poll (calls)`

### `IsolatedMoli::_ready` · line 147

No resolved outgoing call/type edge.

### `IsolatedMoli::_set_environment` · line 155

No resolved outgoing call/type edge.

### `IsolatedMoli::_stop_daemon` · line 169

No resolved outgoing call/type edge.

### `IsolatedMoli::close` · line 183

- `aveli/moli.py:169 IsolatedMoli::_stop_daemon (calls)`
- `aveli/moli.py:183 IsolatedMoli::close (calls)`

### `IsolatedMoli::__exit__` · line 211

- `aveli/moli.py:183 IsolatedMoli::close (calls)`

## `aveli/network.py`

### `_ProxyServer` · line 11

No resolved outgoing call/type edge.

### `_ProxyServer::__init__` · line 14

- `aveli/network.py:14 _ProxyServer::__init__ (calls)`

### `_ProxyHandler` · line 20

No resolved outgoing call/type edge.

### `_ProxyHandler::do_CONNECT` · line 23

No resolved outgoing call/type edge.

### `_ProxyHandler::_deny_http` · line 60

No resolved outgoing call/type edge.

### `_ProxyHandler::log_message` · line 73

No resolved outgoing call/type edge.

### `AllowedHostProxy` · line 77

No resolved outgoing call/type edge.

### `AllowedHostProxy::__init__` · line 78

- `aveli/network.py:11 _ProxyServer (instantiates)`

### `AllowedHostProxy::address` · line 85

No resolved outgoing call/type edge.

### `AllowedHostProxy::__enter__` · line 89

No resolved outgoing call/type edge.

### `AllowedHostProxy::close` · line 93

No resolved outgoing call/type edge.

### `AllowedHostProxy::__exit__` · line 99

- `aveli/network.py:93 AllowedHostProxy::close (calls)`

## `aveli/runner.py`

### `AgentPort` · line 23

No resolved outgoing call/type edge.

### `AgentPort::snapshot` · line 24

No resolved outgoing call/type edge.

### `AgentPort::command` · line 25

No resolved outgoing call/type edge.

### `AgentPort::proposed_action` · line 26

No resolved outgoing call/type edge.

### `AgentPort::close` · line 27

No resolved outgoing call/type edge.

### `JobDeadlineReached` · line 34

No resolved outgoing call/type edge.

### `ProductionRunner` · line 38

No resolved outgoing call/type edge.

### `ProductionRunner::__init__` · line 39

- `aveli/audit.py:17 NullAuditSink (instantiates)`

### `ProductionRunner::_require_isolation` · line 54

- `aveli/isolation.py:21 require_active_isolation (calls)`

### `ProductionRunner::_create_agent` · line 61

- `aveli/agent.py:12 Agent (instantiates)`
- `aveli/runner.py:54 ProductionRunner::_require_isolation (calls)`
- `aveli/runner.py:73 ProductionRunner::_audit_mutation (calls)`

### `ProductionRunner::_audit_mutation` · line 73

- `aveli/audit.py:14 AuditSink::emit (calls)`
- `aveli/job.py:291 PreparedAction::from_proposal (calls)`
- `aveli/job.py:305 PreparedAction::audit_fields (calls)`

### `ProductionRunner::run` · line 81

- `aveli/audit.py:14 AuditSink::emit (calls)`
- `aveli/config.py:76 ProductionSettings::provider_environment (calls)`
- `aveli/job.py:100 VerificationSpec::verify (calls)`
- `aveli/job.py:218 ActionPolicy (instantiates)`
- `aveli/job.py:222 ActionPolicy::check_page (calls)`
- `aveli/job.py:231 ActionPolicy::assess (calls)`
- `aveli/job.py:291 PreparedAction::from_proposal (calls)`
- `aveli/job.py:305 PreparedAction::audit_fields (calls)`
- `aveli/runner.py:173 ProductionRunner::_result (calls)`
- `aveli/runner.py:24 AgentPort::snapshot (calls)`
- `aveli/runner.py:25 AgentPort::command (calls)`
- `aveli/runner.py:26 AgentPort::proposed_action (calls)`
- `aveli/runner.py:27 AgentPort::close (calls)`
- `aveli/runner.py:54 ProductionRunner::_require_isolation (calls)`

### `ProductionRunner::_result` · line 173

- `aveli/audit.py:14 AuditSink::emit (calls)`
- `aveli/job.py:319 _public_url (calls)`
- `aveli/job.py:334 JobResult (instantiates)`
- `aveli/job.py:346 JobResult::to_dict (calls)`

## `aveli/static/app.js`

### `$` · line 1

No resolved outgoing call/type edge.

### `escape` · line 12

No resolved outgoing call/type edge.

### `percent` · line 20

No resolved outgoing call/type edge.

### `call` · line 21

- `aveli/static/app.js:69 render (calls)`

### `controls` · line 33

- `aveli/static/app.js:1 $ (calls)`

### `perform` · line 45

- `aveli/static/app.js:1 $ (calls)`
- `aveli/static/app.js:33 controls (calls)`
- `aveli/static/app.js:69 render (calls)`

### `render` · line 69

- `aveli/static/app.js:1 $ (calls)`
- `aveli/static/app.js:12 escape (calls)`
- `aveli/static/app.js:20 percent (calls)`
- `aveli/static/app.js:33 controls (calls)`

## `aveli/worker.py`

### `WorkerDeadline` · line 19

No resolved outgoing call/type edge.

### `WorkerCancelled` · line 23

No resolved outgoing call/type edge.

### `_deadline_reached` · line 27

- `aveli/worker.py:19 WorkerDeadline (instantiates)`

### `_termination_requested` · line 31

- `aveli/worker.py:23 WorkerCancelled (instantiates)`

### `execute` · line 35

- `aveli/agent.py:199 Agent::run (calls)`
- `aveli/audit.py:22 JsonlAuditSink (instantiates)`
- `aveli/config.py:50 ProductionSettings::from_env (calls)`
- `aveli/isolation.py:35 ChromeConfig::from_env (calls)`
- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `scripts/smoke_worker.py:84 main::runner_factory (calls)`

### `execute::network_denied` · line 52

- `aveli/audit.py:14 AuditSink::emit (calls)`

### `execute::cleanup_failed` · line 55

- `aveli/audit.py:14 AuditSink::emit (calls)`

### `main` · line 68

- `aveli/job.py:346 JobResult::to_dict (calls)`
- `aveli/worker.py:35 execute (calls)`

## `examples/flights.py`

### `verify` · line 18

No resolved outgoing call/type edge.

### `main` · line 41

- `aveli/agent.py:12 Agent (instantiates)`
- `aveli/agent.py:199 Agent::run (calls)`
- `aveli/agent.py:203 Agent::close (calls)`
- `aveli/agent.py:60 Agent::snapshot (calls)`
- `examples/flights.py:18 verify (calls)`

## `scripts/check_deployment.py`

### `require` · line 6

No resolved outgoing call/type edge.

### `main` · line 11

- `scripts/check_deployment.py:6 require (calls)`

## `scripts/check_guards.py`

### `main` · line 17

- `aveli/browser.py:107 Browser::fresh (calls)`
- `aveli/browser.py:119 Browser::act (calls)`
- `aveli/browser.py:130 Browser::close (calls)`
- `aveli/browser.py:21 Browser (instantiates)`
- `aveli/browser.py:48 Browser::call (calls)`
- `aveli/browser.py:51 Browser::evaluate (calls)`
- `aveli/browser.py:57 Browser::observe (calls)`

## `scripts/check_moli.py`

### `check_outcome` · line 15

- `aveli/browser.py:119 Browser::act (calls)`
- `aveli/browser.py:130 Browser::close (calls)`
- `aveli/browser.py:21 Browser (instantiates)`
- `aveli/browser.py:51 Browser::evaluate (calls)`
- `aveli/browser.py:57 Browser::observe (calls)`

### `main` · line 34

- `aveli/moli.py:38 MoliConfig::from_env (calls)`
- `aveli/moli.py:66 IsolatedMoli (instantiates)`
- `scripts/check_moli.py:15 check_outcome (calls)`

## `scripts/check_network_isolation.py`

### `ProbeHandler` · line 11

No resolved outgoing call/type edge.

### `ProbeHandler::do_GET` · line 14

No resolved outgoing call/type edge.

### `ProbeHandler::log_message` · line 20

No resolved outgoing call/type edge.

### `main` · line 24

- `aveli/isolation.py:35 ChromeConfig::from_env (calls)`
- `aveli/isolation.py:90 IsolatedChrome (instantiates)`

## `scripts/check_secrets.py`

### `main` · line 14

No resolved outgoing call/type edge.

## `scripts/check_vulnerabilities.py`

### `main` · line 9

No resolved outgoing call/type edge.

## `scripts/container_healthcheck.py`

### `main` · line 9

- `aveli/isolation.py:35 ChromeConfig::from_env (calls)`

## `scripts/measure_flights.py`

### `timed` · line 34

- `scripts/measure_flights.py:30 raw (calls)`

## `scripts/record_flights.py`

### `capture` · line 36

- `aveli/browser.py:48 Browser::call (calls)`
- `tests/test_isolation.py:24 FakeProcess::wait (calls)`

## `scripts/render_demo.py`

### `font` · line 27

No resolved outgoing call/type edge.

### `mono` · line 31

No resolved outgoing call/type edge.

## `scripts/run_isolated_checks.py`

### `main` · line 10

- `aveli/isolation.py:35 ChromeConfig::from_env (calls)`
- `aveli/isolation.py:90 IsolatedChrome (instantiates)`

## `scripts/smoke.py`

### `main` · line 17

- `aveli/agent.py:12 Agent (instantiates)`
- `aveli/agent.py:199 Agent::run (calls)`
- `aveli/agent.py:60 Agent::snapshot (calls)`
- `aveli/browser.py:51 Browser::evaluate (calls)`
- `aveli/demo.py:23 load_environment (calls)`

## `scripts/smoke_worker.py`

### `NoopChrome` · line 11

No resolved outgoing call/type edge.

### `NoopChrome::__init__` · line 12

No resolved outgoing call/type edge.

### `NoopChrome::__enter__` · line 15

No resolved outgoing call/type edge.

### `NoopChrome::__exit__` · line 22

No resolved outgoing call/type edge.

### `DeniedAgent` · line 28

No resolved outgoing call/type edge.

### `DeniedAgent::__init__` · line 29

No resolved outgoing call/type edge.

### `DeniedAgent::snapshot` · line 38

No resolved outgoing call/type edge.

### `DeniedAgent::command` · line 41

No resolved outgoing call/type edge.

### `DeniedAgent::proposed_action` · line 48

No resolved outgoing call/type edge.

### `DeniedAgent::close` · line 51

No resolved outgoing call/type edge.

### `main` · line 55

- `aveli/job.py:346 JobResult::to_dict (calls)`
- `aveli/worker.py:35 execute (calls)`
- `scripts/smoke_worker.py:28 DeniedAgent (instantiates)`

### `main::runner_factory` · line 84

- `aveli/runner.py:38 ProductionRunner (instantiates)`

## `tests/test_agent.py`

### `page` · line 15

- `aveli/browser.py:136 fingerprint (calls)`

### `choice` · line 32

No resolved outgoing call/type edge.

### `decision` · line 36

No resolved outgoing call/type edge.

### `test_invalid_choice_is_rejected` · line 49

- `aveli/model.py:30 validate_choice (calls)`
- `tests/test_agent.py:32 choice (calls)`

### `test_one_index_per_node_with_operation_specific_targets` · line 67

- `aveli/model.py:48 action_space (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_all_heads_are_one_request_and_only_matching_head_executes` · line 77

- `aveli/model.py:81 choose (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_all_heads_are_one_request_and_only_matching_head_executes::post` · line 80

- `tests/test_agent.py:32 choice (calls)`

### `test_click_cannot_consume_a_text_target` · line 99

- `aveli/model.py:81 choose (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_click_cannot_consume_a_text_target::post` · line 100

- `tests/test_agent.py:32 choice (calls)`

### `test_target_head_receives_control_state_and_full_next_step_rules` · line 116

- `aveli/model.py:81 choose (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_target_head_receives_control_state_and_full_next_step_rules::post` · line 131

- `tests/test_agent.py:32 choice (calls)`

### `test_quoted_task_text_still_uses_the_llm` · line 151

- `aveli/model.py:152 field_context (calls)`
- `aveli/model.py:166 field_text (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_missing_text_credential_stops_before_guessing` · line 162

- `aveli/model.py:166 field_text (calls)`

### `runner` · line 169

- `tests/test_agent.py:15 page (calls)`
- `tests/test_agent.py:36 decision (calls)`

### `test_stale_decision_is_consumed_before_any_mutation` · line 191

- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_generated_text_reused_only_for_identical_retry_context` · line 199

- `aveli/browser.py:17 StalePage (instantiates)`
- `tests/test_agent.py:36 decision (calls)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_changed_field_context_does_not_reuse_generated_text` · line 212

- `aveli/browser.py:17 StalePage (instantiates)`
- `tests/test_agent.py:36 decision (calls)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_loading_waits_do_not_trigger_no_progress_stop` · line 224

- `tests/test_agent.py:36 decision (calls)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_stale_observation_preserves_executed_action` · line 231

- `aveli/browser.py:17 StalePage (instantiates)`
- `tests/test_agent.py:36 decision (calls)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_observation_is_one_atomic_browser_read` · line 240

- `aveli/browser.py:141 browser_operation (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_executor_rejects_a_stale_page_before_browser_input` · line 252

- `aveli/browser.py:119 Browser::act (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_interrupted_dropdown_mutation_cannot_be_retried_as_stale` · line 265

- `aveli/browser.py:141 browser_operation (calls)`

### `test_fingerprint_tracks_values_and_identity_not_screenshots` · line 290

- `aveli/browser.py:136 fingerprint (calls)`
- `tests/test_agent.py:15 page (calls)`

### `test_flight_verification_rejects_wrong_trip` · line 300

- `aveli/job.py:100 VerificationSpec::verify (calls)`

### `test_text_helper_rejects_invalid_values` · line 328

- `aveli/model.py:166 field_text (calls)`

### `test_navigation_during_prediction_reobserves_without_action` · line 335

- `aveli/browser.py:17 StalePage (instantiates)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_mutation_observer_runs_immediately_before_browser_act` · line 343

- `tests/test_agent.py:36 decision (calls)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

### `test_mutation_observer_runs_immediately_before_browser_act::browser_act` · line 348

No resolved outgoing call/type edge.

### `test_changed_node_identity_does_not_reuse_generated_text` · line 358

- `aveli/browser.py:17 StalePage (instantiates)`
- `tests/test_agent.py:36 decision (calls)`
- `tests/test_runner.py:191 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command (calls)`

## `tests/test_browser.py`

### `observed` · line 9

No resolved outgoing call/type edge.

### `test_initial_observation_retries_until_page_controls_exist` · line 22

- `aveli/browser.py:57 Browser::observe (calls)`
- `tests/test_browser.py:9 observed (calls)`

### `test_initial_observation_of_control_free_page_is_bounded` · line 36

- `aveli/browser.py:57 Browser::observe (calls)`
- `tests/test_browser.py:9 observed (calls)`

### `test_screenshot_timeout_preserves_structured_observation` · line 48

- `aveli/browser.py:141 browser_operation (calls)`
- `tests/test_browser.py:9 observed (calls)`

### `test_screenshot_timeout_preserves_structured_observation::cdp` · line 51

No resolved outgoing call/type edge.

### `test_select_requires_an_observed_option_identity` · line 64

- `aveli/browser.py:141 browser_operation (calls)`

### `test_select_passes_exact_option_identity_to_executor` · line 71

- `aveli/browser.py:141 browser_operation (calls)`

### `test_select_passes_exact_option_identity_to_executor::cdp` · line 82

No resolved outgoing call/type edge.

### `test_partial_browser_startup_closes_created_target` · line 93

- `aveli/browser.py:21 Browser (instantiates)`

### `test_partial_browser_startup_closes_created_target::cdp` · line 96

No resolved outgoing call/type edge.

### `test_before_mutation_runs_after_freshness_and_immediately_before_operation` · line 111

- `aveli/browser.py:119 Browser::act (calls)`

### `test_stale_action_never_records_mutation_intent` · line 128

- `aveli/browser.py:119 Browser::act (calls)`

## `tests/test_config.py`

### `valid_env` · line 6

No resolved outgoing call/type edge.

### `test_production_settings_parse_valid_environment` · line 19

- `aveli/config.py:50 ProductionSettings::from_env (calls)`
- `tests/test_config.py:6 valid_env (calls)`

### `test_production_settings_fail_closed` · line 36

- `aveli/config.py:50 ProductionSettings::from_env (calls)`
- `tests/test_config.py:6 valid_env (calls)`

## `tests/test_isolation.py`

### `FakeProcess` · line 10

No resolved outgoing call/type edge.

### `FakeProcess::__init__` · line 11

No resolved outgoing call/type edge.

### `FakeProcess::poll` · line 17

No resolved outgoing call/type edge.

### `FakeProcess::terminate` · line 20

No resolved outgoing call/type edge.

### `FakeProcess::wait` · line 24

No resolved outgoing call/type edge.

### `FakeProcess::kill` · line 29

No resolved outgoing call/type edge.

### `fake_terminate` · line 34

- `tests/test_isolation.py:20 FakeProcess::terminate (calls)`

### `fake_popen` · line 38

No resolved outgoing call/type edge.

### `fake_popen::launch` · line 39

- `tests/test_isolation.py:10 FakeProcess (instantiates)`

### `test_isolation_sets_explicit_endpoint_and_unique_runtime_then_cleans` · line 51

- `aveli/isolation.py:28 ChromeConfig (instantiates)`
- `aveli/isolation.py:90 IsolatedChrome (instantiates)`
- `tests/test_isolation.py:38 fake_popen (calls)`

### `test_isolation_cleans_up_when_job_fails` · line 73

- `aveli/isolation.py:28 ChromeConfig (instantiates)`
- `aveli/isolation.py:90 IsolatedChrome (instantiates)`
- `tests/test_isolation.py:38 fake_popen (calls)`

### `test_chrome_config_requires_real_explicit_binary` · line 85

- `aveli/isolation.py:35 ChromeConfig::from_env (calls)`

### `test_chrome_forces_loopback_through_allowlist_proxy` · line 91

- `aveli/isolation.py:28 ChromeConfig (instantiates)`
- `aveli/isolation.py:90 IsolatedChrome (instantiates)`
- `tests/test_isolation.py:38 fake_popen (calls)`

### `test_process_group_is_terminated` · line 107

- `aveli/isolation.py:62 _terminate_process_group (calls)`
- `tests/test_isolation.py:10 FakeProcess (instantiates)`

### `test_process_group_is_terminated::killpg` · line 111

No resolved outgoing call/type edge.

## `tests/test_job.py`

### `payload` · line 12

No resolved outgoing call/type edge.

### `test_job_spec_parses_to_immutable_validated_types` · line 31

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_job_spec_rejects_unsafe_or_unverifiable_inputs` · line 50

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_policy_classifies_and_restricts_hosts_and_actions` · line 57

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `aveli/job.py:218 ActionPolicy (instantiates)`
- `aveli/job.py:231 ActionPolicy::assess (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_verification_requires_all_declared_evidence` · line 76

- `aveli/job.py:100 VerificationSpec::verify (calls)`
- `aveli/job.py:81 VerificationSpec::from_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_unknown_action_kind_fails_closed` · line 98

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `aveli/job.py:218 ActionPolicy (instantiates)`
- `aveli/job.py:231 ActionPolicy::assess (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_unsafe_job_id_is_rejected` · line 105

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_loopback_and_non_default_ports_are_rejected` · line 112

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_type_text_cannot_use_the_approval_path_without_exact_preparation` · line 121

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_verification_output_does_not_repeat_expected_secrets` · line 129

- `aveli/job.py:100 VerificationSpec::verify (calls)`
- `aveli/job.py:81 VerificationSpec::from_dict (calls)`

### `test_download_is_not_misclassified_as_navigation` · line 136

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `aveli/job.py:218 ActionPolicy (instantiates)`
- `aveli/job.py:231 ActionPolicy::assess (calls)`
- `tests/test_job.py:12 payload (calls)`

### `test_job_and_result_contracts_are_versioned` · line 145

- `aveli/job.py:138 JobSpec::from_dict (calls)`
- `aveli/job.py:334 JobResult (instantiates)`
- `aveli/job.py:346 JobResult::to_dict (calls)`
- `tests/test_job.py:12 payload (calls)`

## `tests/test_moli.py`

### `FakeProcess` · line 10

No resolved outgoing call/type edge.

### `FakeProcess::__init__` · line 11

No resolved outgoing call/type edge.

### `FakeProcess::poll` · line 15

No resolved outgoing call/type edge.

### `FakeProcess::terminate` · line 18

No resolved outgoing call/type edge.

### `fake_moli` · line 22

No resolved outgoing call/type edge.

### `fake_terminate` · line 28

- `tests/test_moli.py:18 FakeProcess::terminate (calls)`

### `test_config_requires_an_existing_moli_binary` · line 32

- `aveli/moli.py:38 MoliConfig::from_env (calls)`

### `test_config_requires_pinned_moli_version` · line 37

- `aveli/moli.py:38 MoliConfig::from_env (calls)`
- `tests/test_moli.py:22 fake_moli (calls)`

### `test_config_accepts_exact_pinned_moli_version` · line 43

- `aveli/moli.py:38 MoliConfig::from_env (calls)`
- `tests/test_moli.py:22 fake_moli (calls)`

### `test_isolated_moli_uses_real_layout_and_restores_environment` · line 48

- `aveli/moli.py:30 MoliConfig (instantiates)`
- `aveli/moli.py:66 IsolatedMoli (instantiates)`
- `tests/test_moli.py:10 FakeProcess (instantiates)`

### `test_startup_timeout_is_bounded_without_process_output` · line 83

- `aveli/moli.py:30 MoliConfig (instantiates)`
- `aveli/moli.py:66 IsolatedMoli (instantiates)`
- `tests/test_moli.py:10 FakeProcess (instantiates)`

## `tests/test_network.py`

### `request` · line 6

No resolved outgoing call/type edge.

### `test_proxy_denies_undeclared_connect_without_contacting_destination` · line 12

- `aveli/network.py:77 AllowedHostProxy (instantiates)`
- `tests/test_network.py:6 request (calls)`

### `test_proxy_denies_plain_http_and_non_tls_ports` · line 20

- `aveli/network.py:77 AllowedHostProxy (instantiates)`
- `tests/test_network.py:6 request (calls)`

## `tests/test_runner.py`

### `active_isolation` · line 11

No resolved outgoing call/type edge.

### `settings` · line 20

- `aveli/config.py:36 ProductionSettings (instantiates)`

### `job` · line 32

- `aveli/job.py:138 JobSpec::from_dict (calls)`

### `FakeAgent` · line 49

No resolved outgoing call/type edge.

### `FakeAgent::__init__` · line 50

No resolved outgoing call/type edge.

### `FakeAgent::snapshot` · line 63

No resolved outgoing call/type edge.

### `FakeAgent::command` · line 66

No resolved outgoing call/type edge.

### `FakeAgent::proposed_action` · line 84

No resolved outgoing call/type edge.

### `FakeAgent::close` · line 87

No resolved outgoing call/type edge.

### `proposal` · line 91

No resolved outgoing call/type edge.

### `terminal` · line 95

No resolved outgoing call/type edge.

### `result_page` · line 99

No resolved outgoing call/type edge.

### `test_policy_denial_stops_before_browser_mutation` · line 103

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_cross_host_navigation_is_denied_before_browser_mutation` · line 111

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_approval_required_action_denies_without_provider` · line 119

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_approved_action_executes_then_independent_verification_passes` · line 127

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `aveli/runner.py:81 ProductionRunner::run (calls)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_runner.py:95 terminal (calls)`
- `tests/test_runner.py:99 result_page (calls)`

### `test_model_done_is_not_success_when_verification_fails` · line 137

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:95 terminal (calls)`
- `tests/test_runner.py:99 result_page (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_post_action_cross_host_redirect_stops_job` · line 145

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_runner.py:99 result_page (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `RecordingAudit` · line 153

No resolved outgoing call/type edge.

### `RecordingAudit::__init__` · line 154

No resolved outgoing call/type edge.

### `RecordingAudit::emit` · line 157

No resolved outgoing call/type edge.

### `test_execution_intent_is_audited_before_browser_mutation` · line 161

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:153 RecordingAudit (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_runner.py:95 terminal (calls)`
- `tests/test_runner.py:99 result_page (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_execution_intent_is_audited_before_browser_mutation::command` · line 167

No resolved outgoing call/type edge.

### `test_slow_prediction_cannot_mutate_after_deadline` · line 178

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_hard_worker_deadline_escapes_runner_and_still_closes_agent` · line 187

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:190 test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:95 terminal (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent` · line 190

- `tests/test_runner.py:49 FakeAgent (extends)`

### `test_hard_worker_deadline_escapes_runner_and_still_closes_agent::DeadlineAgent::command` · line 191

- `aveli/worker.py:19 WorkerDeadline (instantiates)`

### `test_default_production_agent_requires_active_isolation` · line 200

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `aveli/runner.py:61 ProductionRunner::_create_agent (calls)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`

### `test_default_production_agent_requires_active_isolation::missing` · line 201

No resolved outgoing call/type edge.

### `test_approval_receives_frozen_exact_action` · line 210

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:91 proposal (calls)`
- `tests/test_runner.py:95 terminal (calls)`
- `tests/test_runner.py:99 result_page (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_approval_receives_frozen_exact_action::approve` · line 217

No resolved outgoing call/type edge.

### `test_public_result_url_removes_path_query_and_fragment` · line 228

- `aveli/job.py:346 JobResult::to_dict (calls)`
- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`
- `tests/test_runner.py:49 FakeAgent (instantiates)`
- `tests/test_runner.py:95 terminal (calls)`
- `tests/test_runner.py:99 result_page (calls)`
- `tests/test_worker.py:58 FakeRunner::run (calls)`

### `test_active_isolation_hosts_must_exactly_match_job` · line 238

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `aveli/runner.py:61 ProductionRunner::_create_agent (calls)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`

### `test_final_pre_mutation_hook_enforces_deadline` · line 249

- `aveli/runner.py:38 ProductionRunner (instantiates)`
- `aveli/runner.py:73 ProductionRunner::_audit_mutation (calls)`
- `tests/test_runner.py:20 settings (calls)`
- `tests/test_runner.py:32 job (calls)`

## `tests/test_worker.py`

### `environment` · line 9

No resolved outgoing call/type edge.

### `payload` · line 24

No resolved outgoing call/type edge.

### `FakeChrome` · line 39

No resolved outgoing call/type edge.

### `FakeChrome::__init__` · line 42

No resolved outgoing call/type edge.

### `FakeChrome::__enter__` · line 46

No resolved outgoing call/type edge.

### `FakeChrome::__exit__` · line 50

No resolved outgoing call/type edge.

### `FakeRunner` · line 54

No resolved outgoing call/type edge.

### `FakeRunner::__init__` · line 55

No resolved outgoing call/type edge.

### `FakeRunner::run` · line 58

- `aveli/job.py:334 JobResult (instantiates)`
- `aveli/job.py:67 VerificationOutcome (instantiates)`
- `tests/test_runner.py:157 RecordingAudit::emit (calls)`

### `test_execute_uses_isolation_and_writes_redacted_audit` · line 78

- `aveli/worker.py:35 execute (calls)`
- `tests/test_worker.py:24 payload (calls)`
- `tests/test_worker.py:9 environment (calls)`

### `test_main_returns_machine_readable_failure_for_invalid_json` · line 93

- `aveli/demo.py:131 main (calls)`

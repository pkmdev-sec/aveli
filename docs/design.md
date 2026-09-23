# Operation and target selection

The input is one natural-language goal. Each page observation creates an indexed table of visible controls and their current values. One node gets one index, even when it supports more than one operation.

One TypeSafe request asks for an operation and a compatible target for each available operation. The executor uses only the target that matches the selected operation. This design avoids a second model request and rejects incompatible targets. Dropdown targets include an option index owned by the code.

Operation and target questions receive the same next-step rules. Target criteria include current values and checked or selected state. The questions run independently, so each target question names the operation it assumes.

`TYPE_TEXT` sends the goal, selected field, visible page context, and recent actions to a text model. The response must be JSON with exactly one valid `text` value. Aveli does not copy quoted text from the goal. It can reuse a value after a stale decision only when the complete text-helper input is unchanged. A successful mutation clears the cached value.

## Runtime

One browser-side DOM snapshot provides common HTML and ARIA roles, names, values, visible text, and executable targets. A `WeakMap` gives each DOM node an identity owned by Aveli. A `Map` keeps the live references used for execution. Replaced elements get new identities. Aveli removes disconnected references, and navigation starts a new cache. These identities are not CDP backend node IDs. The browser reads geometry again immediately before input.

The model sees visible text. Focus emulation keeps animation frames running in the owned background tab. Library calls disable screenshots by default. Set `screenshots=True` or `record_dir=...` to enable them. The inspector enables screenshots. A separate continuous screencast can record a run.

Freshness checks compare semantic state rather than DOM mutation counts. Before a click or selection, Aveli compares the document, full URL, viewport, safe form values and states, selected target, and nearby form, dialog, or row context. Text generation, typing, scrolling, waiting, and completion use a full semantic comparison. The executor checks visibility, enabled state, geometry, and click occlusion again before input. Scoped checks permit unrelated visible content to change. This is a practical rule, not proof that the change is irrelevant to the goal.

Aveli does not retry browser mutations after transport recovery. It logs a completed action before the next observation, including when that observation sees a navigation. An interrupted native selection stops because its change event may already have fired. Typing uses the browser's select-all command and CDP text insertion to replace existing input.

After an interaction, Aveli waits for up to two animation frames or 50 ms. Editable ARIA comboboxes instead wait up to 200 ms for visible options. This prevents a prediction before autocomplete results appear. An explicit `WAIT` lasts 100 ms. Recordings preserve network loading time.

## Changes since the first demo

The first prototype used five prepared steps and copied quoted strings. It proved finite-choice browser execution, but it did not prove task decomposition or text generation. The current policy uses the original goal throughout. Operation and target distributions replace the old flat-choice and lookahead design.

The first implementation also treated every `INPUT` element as editable, which misclassified checkboxes. Editable roles now control `TYPE_TEXT` availability. Tests cover control classification, invalid model output, stale decisions, text-cache invalidation, missing credentials, waits, and final-route verification.

## Boundaries

A run allows at most 60 browser actions and 120 decision requests. Aveli retains up to 250 action candidates, and the model cannot select truncated candidates. The inspector listens only on loopback, serializes actions, and checks `Host`, `Origin`, and a local request token. Credentials remain on the server. Tabs share the existing Chrome profile.

The policy is generic, but two websites do not establish broad reliability. Name resolution handles common labels, ARIA references, and text. It does not implement the browser's full accessible-name algorithm. Shadow roots, frames, canvas, uploads, nested scrolling, pop-ups, and complex keyboard interactions can stop a task. A valid action can still be wrong. Independent checks determine whether a task succeeded. The model's `DONE` choice does not.

# Agent instructions (scope: this directory and subdirectories)

## Mission

- This repository is a visual, practical curriculum for learning Google ADK
  design patterns and producing lessons for a Skool community.
- Each pattern should progress through: understand the visual, build privately,
  test, evaluate, verify, reset to a clean starting point, and rebuild while
  screen-recording.
- Optimize examples for reproducibility, employable skills, and clear business
  value.

## Repository map

| Path | Purpose |
|---|---|
| `visuals/` | Prioritized ADK orchestration-pattern lessons and PNG diagrams |
| `examples/` | Independently scaffolded, runnable lesson projects |
| `additional-patterns-worth-exploring/` | Deferred topics that are not current priorities |
| `README.md` | Pattern catalog, scope, and decision map |

## Collaboration mode

- The user operates the terminal and writes the lesson implementation.
- Coach one checkpoint at a time: explain the goal, provide the command or
  coding task, wait for the result, and help interpret it.
- Do not create, edit, or replace example code unless the user explicitly asks
  for implementation help.
- Read-only inspection is allowed when needed to explain structure or diagnose
  a result.
- When the user is stuck, reproduce and localize one issue before proposing one
  focused change.
- Preserve the user's model, environment variables, configuration, and
  unrelated code unless a change is explicitly requested.

## Google ADK workflow

- Follow the installed `google-agents-cli-workflow` phases:
  understand, study samples, scaffold, build, evaluate, deploy, publish, and
  observe.
- Before creating a project, inspect relevant reference samples and run
  `agents-cli info`.
- Use `agents-cli scaffold create`; do not manually create its target directory.
- Use `AGENTS.md` as the scaffold guidance filename when the CLI supports that
  option.
- Start lessons as local prototypes. Do not add deployment, CI/CD, a Git remote,
  or cloud resources without explicit approval.
- Use `uv` for Python setup and execution.
- Use `agents-cli run` for smoke tests and `agents-cli eval` for behavioral
  validation.
- Use pytest only for deterministic code behavior; never assert exact LLM
  wording with pytest.

## Current lesson

- **Pattern:** Sequential pipeline.
- **Project:** Qualified fitness-client onboarding.
- **Intended project path:** `examples/fitness-onboarding/`.
- **Status:** Scaffolded and implemented locally; verification evidence and
  lesson commands live in `examples/fitness-onboarding/README.md`.
- **Runtime scope:** Local Python prototype using ADK agents and local tools.
- **External services:** None initially.
- **Safety:** Do not diagnose or prescribe medical treatment, invent client
  details, send real email, or perform external side effects.

### Intended fixed sequence

1. Intake agent validates and normalizes the qualified client's form.
2. Consultation agent prepares a coach briefing and consultation plan.
3. Welcome agent creates a mock booking link and welcome-email draft.
4. The sequence returns a structured onboarding package.

- Keep this lesson genuinely sequential: every stage runs in a fixed order.
- Qualification branching belongs in the later conditional-routing lesson.
- Use a deterministic local tool for mock booking-link creation.

### Implemented lesson architecture

- `app/agent.py` is the ADK composition root and exports `root_agent` and `app`.
- `app/agents/` contains builder classes for the three stages and root sequence.
- `app/models/` contains the client, prompt, and tool-result contracts.
- `app/prompts/` contains one versioned YAML prompt per LLM agent.
- `app/tools/` contains deterministic intake, booking, and email functions.
- The final agent responds naturally; structured validation, booking, and email
  results remain available in session state and tool traces.
- Invalid intake uses agent-level rejection: all stages are entered, but later
  prompts must avoid booking and email tools.

### Graph migration lesson

- **Project:** `examples/fitness-onboarding-graph/`
- **Root:** `Workflow(name="fitness_onboarding_graph")`
- Reuses the same qualified-client business scenario so learners can compare
  orchestration rather than domain logic.
- Validation routes valid input to consultation and invalid input directly to a
  terminal correction node.
- Booking and email are explicit deterministic function nodes, not LLM-selected
  tools.
- The invalid terminal node has no path to booking or email.
- The project remains a local prototype with no deployment, CI/CD, Terraform,
  or external integrations.

## Design principles for lesson code

- Prefer composition over deep inheritance; ADK already composes agents,
  workflows, and tools.
- **Encapsulation:** Keep business rules and provider details out of prompts and
  agent construction.
- **Abstraction:** Define small contracts around capabilities that may change,
  such as booking-link generation.
- **Polymorphism:** Make it possible to replace a mock provider with a real
  provider without changing agent behavior.
- **Inheritance:** Use only for a stable shared contract or framework extension;
  do not introduce class hierarchies merely to demonstrate OOP vocabulary.
- Keep tools thin, typed, documented, deterministic where possible, and
  JSON-serializable.
- Keep agent construction separate from domain and integration logic.

## Lesson verification

- Verify that all sequential stages run in order.
- Verify that downstream stages consume upstream outputs.
- Verify that the booking-link tool is invoked.
- Verify that client constraints remain present in the final package.
- Verify that the output does not invent client facts or provide medical advice.
- Save exact commands, representative prompts, expected traces, evaluation
  results, and common failure modes for the recorded lesson.

## Visual and documentation conventions

- Each prioritized pattern lives in `visuals/<pattern>/` with a `README.md` and a
  matching PNG.
- Keep deferred patterns outside `visuals/` until they are intentionally
  prioritized.
- Document public modules, classes, and functions when their responsibility or
  contract is not obvious.
- Update nearby lesson documentation when behavior changes; delete stale
  instructions in the same change.
- Never store secrets, credentials, or real client information in examples,
  tests, screenshots, traces, or documentation.

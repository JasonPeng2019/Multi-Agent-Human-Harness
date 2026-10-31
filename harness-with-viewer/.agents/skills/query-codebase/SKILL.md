---
name: query-codebase
description: Answer structural codebase questions from repository evidence instead of memory: definitions, references, callers, imports, ownership, reachability, dependencies, and whether code is used. Read-only; use before assuming how unfamiliar code is wired.
---

# Query the codebase from evidence

Translate the question into the smallest reliable read-only query.

1. Establish the repository root and requested scope.
2. Prefer `rg`/`rg --files` for text, symbols, and file discovery.
3. Use Git for tracked state, history, blame, and diff questions.
4. Use an existing language analyzer for type, call, import, or dependency
   questions only when its project configuration is already authoritative.
5. Follow references far enough to answer the question, not to dump the entire
   repository.
6. Rerun observations if source changes before relying on them.

For repositories containing submodules or nested Git roots, identify the boundary
and label uninitialized or inaccessible repositories as opaque. Do not initialize,
clone, update, or execute repository-controlled tooling without authorization.

Return:

- the answer in plain language;
- exact supporting file/line locations;
- commands or analyzer used when relevant;
- ambiguity, opaque areas, or limitations.

Do not edit files. Do not infer “unused,” “unreachable,” or “only caller” from one
text search when dynamic registration, generated code, reflection, templates, or
another repository can plausibly participate.

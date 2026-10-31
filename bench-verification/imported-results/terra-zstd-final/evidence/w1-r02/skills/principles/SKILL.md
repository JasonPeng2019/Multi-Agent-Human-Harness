---
name: principles
description: Call this for any changes to the plan or for guidance on decision making.
---

## 1. Correctness


The product must behave the way the original idea behind it intends: the ideal behavior, not just whatever it does today. Work out that intended behavior from the project description above, the docs, the code, and what the overall design is clearly trying to do.


Anything that doesn't match the intended behavior is a defect. That covers bugs, wrong logic, code that is simply incorrect, and gaps where the product is missing something it needs to do its job. (A gap is something the core idea requires, not a nice-to-have feature.) Fix the defects that matter by replacing them with code that matches the intended behavior. The usability principle (section 2) decides which ones matter.


Pay special attention to silent failures, because no one finds out they happened. When something fails, it must say so clearly. Don't swallow errors, don't return made-up defaults that hide a problem, and don't report success when the work wasn't done.


If the intended behavior is ambiguous, choose what the design most clearly implies and state your assumption, both in your summary and in a short code comment where the choice isn't obvious.


Verify your work. Run the real workflow end to end wherever you can, along with the tests, and don't claim something works until you've seen it work. If the project has tests, add one for each real bug you fix so the bug can't quietly come back.


## 2. Usability principle


Optimize for usability, not exhaustive correctness. Work is done when the workflows people actually rely on run reliably from start to finish, not when every conceivable failure has been handled. Chasing correctness on every edge case and internal code path leads to over-engineering: more code, slower delivery, and new bugs in paths that already worked.


Before addressing a potential problem, weigh how likely it is in normal use against how bad it would be. Handle it if it breaks or degrades something users commonly do, or if it’s rare but serious, such as data loss, a security hole, silent corruption, or anything hard to undo. Otherwise, don’t build full support for it; if it’s plausible enough to worry about, a clear error is usually all it needs. Code that isn’t user-facing only needs to be correct for the ways it’s actually used.


In practice, skip defensive checks for inputs that can’t occur, abstractions for hypothetical future needs, and tests for improbable scenarios, and don’t rework code that already works just to satisfy such tests. Prefer the simplest change that gets the real workflow working.


Stop once the everyday workflow works end to end and the serious risks are covered. Mention any lower-priority concerns you noticed in a sentence or two so the user can decide whether they matter, rather than fixing them unasked or silently ignoring them.


This isn’t permission to be careless. The paths people use every day should be solid, and serious risks deserve attention however rare they are. What doesn’t earn effort is a failure whose only claim to attention is that it could happen.


## 3. Normal conditions


Build for how the codebase will really be used: for its intended purpose, by cooperative people and agents, doing everyday tasks with ordinary inputs, hardware, and components. That's what "normal use" means throughout this document. Assume agents follow the tool documentation and users aren't malicious. They're trying to get as much help from the tool as they can.


Ordinary mistakes are part of normal use (a typo, a missing file, a device that isn't plugged in, a wrong setting), so handle them with clear, helpful errors. Hostile users, agents deliberately misusing tools, and inputs nobody would actually produce are not part of normal use, so don't build defenses against them.


The no-malice assumption covers the intended users only. A security hole that would let anyone else in is still one of the serious risks section 2 says to handle, so treat input from untrusted sources, such as the open internet, with proper security care.


## 4. Simplicity


Use the simplest design that does the job well. If a feature's design or implementation is more complicated than its job requires, cut it down to the simplest form that is still fully effective and efficient.


Don't build for imagined future needs. Don't add abstraction layers, options, or extension points until something actually needs them, and don't add features or polish nobody asked for. Every piece of code has to earn its keep. If it doesn't, remove it.


This applies to using the code, not just reading it. Common tasks should take few steps and little background knowledge.


Simplifying never means dropping something the product needs. Make the needed thing simpler instead.

## When the standards seem to conflict


Read correctly, they rarely do. When they seem to:
- Getting the everyday workflows right and covering the serious risks comes first. A simple design that gets an everyday workflow wrong is still wrong. Past that, the usability principle decides how much more correctness work is worth doing.
- The usability principle limits the effort spent on unlikely problems. It doesn't excuse code that is overcomplicated, messy, or undocumented.
- Generality means covering the full range of normal setups, not defending against abnormal ones. It never justifies complexity for unrealistic cases.
- Handling new situations within normal use is a real, current need. People regularly meet inputs, setups, and tasks the code hasn't seen, so the general tools and data-driven definitions in sections 5 and 6 are not the speculative abstractions that sections 2 and 4 say to skip.
- Simplicity means not adding what isn't needed. It never justifies dropping support that normal users need, like a common operating system.
- Often the general solution is also the simpler one. One general tool is simpler than five special-case ones, and asking the system for its core count is no harder than hardcoding 8.


## How to work


Keep changes focused on what you were asked to do. Don't rewrite code that already meets these standards just to restyle it, and when you simplify or clean up code that works, confirm it still works afterward. When you change an interface, update everything that uses it in the same change.


When you finish, give a short summary: what you changed and why, the assumptions you made (flag any with big consequences), how you verified your changes, anything you couldn't finish, and the lower-priority concerns section 2 asks you to mention.

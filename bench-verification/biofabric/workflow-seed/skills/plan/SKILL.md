---
name: plan
description: Make a plan for a software request. Defines the requirements and expectations of the minimal working product that satisfies the request, then breaks it into direct, simple, and manageable tasks with one deliverable each, where each task has its own module plan file under .plans. Use this to plan any request to build, add, or change code.
---

# Plan

A plan has two parts, in this order: the definition of the minimal working product, then the tasks that build it.

## 1. Define the minimal working product

First, define the requirements and expectations of the minimal working product that satisfies the request.

The minimal working product is the smallest version of what was asked for that fully works. Minimal means it includes only what the request needs. Working means it actually does what was asked, not just part of it.

- **Requirements:** what the product must do to satisfy the request. Make each one specific, and include only what the request needs.
- **Expectations:** what should happen when the product works, meaning the results someone would see when using it. Make each one concrete enough that you can tell whether it's met.

## 2. Break it into tasks

Break the minimal working product into tasks. Together, the tasks build exactly the product defined in step 1.

Each task is:

- **Direct:** it goes straight at its part of the product, with no side work.
- **Simple:** it's done in the most straightforward way that works.
- **Manageable:** it's small enough to complete in one go.
- **One deliverable:** it produces exactly one result.

If a task would produce more than one deliverable, or is too big to complete in one go, split it.

A module is a manageable unit of work. If the work can be split into multiple concrete, simple, direct tasks, split those tasks into modules, each with its own module file under a .plans folder. A module is a manageable unit of work, not necessarily a separate source file. Multiple modules may incrementally modify the same file

Write each module file with one objective, inputs, one deliverable, and acceptance criteria.

## Plan format

```markdown
## Minimal working product

**Requirements**
- <requirement>

**Expectations**
- <expectation>

## Tasks

1. <what the task does>
   - Module file: `.plans/<module>.md`
   - Deliverable: <the task's one deliverable>
```

## Example

Request: "Make a command-line tool that checks which URLs in a text file are down."

```markdown
## Minimal working product

**Requirements**
- Reads a text file with one URL per line.
- Checks whether each URL responds.
- Prints each URL with "up" or "down."

**Expectations**
- Running `python main.py urls.txt` on a file with one working URL and one broken URL prints the first as up and the second as down.
- Every URL in the file gets checked, even after one is down.

## Tasks

1. Read the URL list.
   - Module file: `.plans/read-urls.md`
   - Deliverable: a function that returns the URLs in a file
2. Check one URL.
   - Module file: `.plans/check-url.md`
   - Deliverable: a function that returns whether a URL responds
3. Run the tool.
   - Module file: `.plans/run-tool.md`
   - Deliverable: a command that reads the file, checks each URL, and prints the results
```

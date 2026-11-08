# Brainstorm transcript — aitm Python rewrite (2026-11-08)

Source: Claude Code session 7046edcc-744e-49cf-847a-549bc0ec11ba (ai-task-manager worktree python-rewrite-backlog-state). User and assistant prose only; tool calls and tool output omitted.

## User

read thru the code on this project, and thru the open stories...  I want to look into a re-write of the entire product using python.  I am guessing that we can get a better runtime using python while still keeping the installation simple.  This product is a collection of tools that should be called thru an MCP or a plugin.  The MCP is likely just markdown directives to the agent.  The archestrator CLI and all the state management tools would be python scripts.

My first look will be to replace the state machine for the workflow of stories from backlog to done.  We will need a translation of the init tool that creates a github project to watch the stories advance thru the state-machine.  Since there is a limit on github gql calls for managing the backlog I will want a local backlog datastore that allows a more detailed data entry for each backlog item, and allows a constant and simple access for CRUD to that datastore.  The datastore should be committed to git history .  All story details should be committed to a planning branch and merged to the default branch so github stories can hold references to the commit sha and file path,  although we should investigate if this is also possible using commits to a story branch pushed to origin and have the github issue reference to the story details follow the commit migration from story branch to default branch.  The challenge here is any form of rebase will change the commit shal I want to be able to load the story in the github UI and click a link for the story details file and see it in the github viewer ( whether the latest version of the story file is in the story branch or default branch).  If the story is abandoned and the working branch deleted I will still want to see the story in the history with an explanation as to why it was abandoned.

Every data file for a story should have a frontmatter section explaining the story id (as defined in github issue), creation date, last update timestamp, last working branch and worktree location, story estimate and any references to extra datafiles that relate to the story.

The current aitm uses hidden comments in the story markdown to record markers for story progress.  I want to use embedded json for all markers, enclosing collections of markers in `<details><summary>...</summary></details>` blocks to make them hidden but expandable on demand when viewing the data file in the github UI.

The recorded story file should contain a link to quickly reference the github issue in the github UI.

Because we have alot of data that is generated in the story tracking it's progress thru the state machine with timestamp markers and updates for new tests and test runs etc -- we will be building most of this into the local data files and pushing the contents to origin with merge to trunk and updating the github issue with necessary references on a sparse cadence -- likely on state change ( i.e Plan -> Develop, Develop->Test...); this will reduce the abuse of the GQL api limits.

With all of the data stored locally in the git history we should be able to easily mine the data for extraneous information during planning and estimating of other stories.  One feature we want to build stronger is the estimation rubric, expanding to a planning and estimation rubric.  I want Machine Learning involved on how to better design and plan epics and stories -- keeping all leaf stories no larger than 4 hr of estimated agent engagement.  Planning for human effort is no longer valuable as the industry is rotating towards all agent written code.  When a story is planned and estimated it should learn from the past when a fully planned, reviewed and accepted story encounters defects, or expands beyond the 4 hr time limit, or finds discovered work (all these events should be recorded in the frontmatter of the story record in a data dense format optimized for the agent) The agent must learn how to design, plan and estimate work better from every story committed to history.  If possible we should make this planning / estimating rubric a plugin to the system that can be deployed separately and incorporated when installing the tool set.

Actually , I think it might be an optimization to have many features like the planning/estimating rubric, github issue management, and a local story viewer (hosted UI that allows me to view the complete story details in a intuitive, data rich web page similar to the github project view
(`https://github.com/users/kburson/projects/11/views/6`) with extra features for visualizing feature flow thru the state machine - mining the data from the git history.  Possibly deploying this web app to a github pages location so it can be access online as well as locally.

Once you collect the data on all of this we will need to brainstorm an optimal structure, stack, phased development.  We are using a worktree and can generate a story for this brainstorming and planning phase, but it is most likely we will build this in a separate git repo that will eventually replace the current one.

The problem with the current repo is that it is being buried under it's own weight.  Stories are taking too long and hitting way too many blockers that prevent an efficient progress thru the backlog items -- I am looking at abandoning the current build for a new one, and I am hoping the python code rather than the javascript code will make it faster, more efficient and give me a chance to learn python.

## Assistant

Surveying the init/project-creation path and body-marker formats next.

## Assistant

Reading the existing design specs for local backlog (#1817), estimation rubric (#1821), and MCP architecture (#1725).

## Assistant

Pulling issue-history metrics to quantify the "buried under its own weight" problem.

## Assistant

# Findings: a Python rewrite of aitm

## 1. Why the current repo is slow

**Size**
- 193k lines of source plus 342k lines of tests, across 2,547 files under `scripts/`.
- 373 modules in `lib/`, 49 of which are guards. 161 different `aitm-*` marker names.
- `verbs/close.mjs` alone is 5,433 lines. There are 2,035 files under `docs/`.

**Throughput has collapsed**

| Month | Commits | Issues created | Of which bugs | Issues closed |
|---|---|---|---|---|
| Aug | 810 | 280 | 139 | 269 |
| Sep | 257 | 236 | 64 | 196 |
| Oct | 87 | 165 | 113 (68%) | 103 |

**Root cause:** the issue body on GitHub is the main database. Markers are parsed with regexes, and every write has to fetch, diff, verify, lock and fence. The open backlog shows it: most titles are about recovery, sagas, revision fences, ledgers, idempotent repair and custody. The product has been building transaction infrastructure around a datastore it doesn't control.

Your design fixes that by making git the authority and GitHub a one-way projection. If a sync fails, you just re-run it, so that whole class of bugs goes away.

## 2. Python: be honest about where the speed comes from

- **The language won't make it faster.** The bash-guard hook takes about 139ms on Node; a bare Python start with imports takes about 88ms. For raw compute, CPython is slower than V8. The speedup comes from fewer process spawns, reading local files instead of calling the API, and far fewer guards.
- **Real reasons to choose Python:**
  - It's a good chance for you to learn it.
  - One-command install with `uv` / `uvx`.
  - The ML libraries (scikit-learn and others) you'll want for the rubric.
  - Plugin discovery through `importlib.metadata` entry points, which suits separately deployed plugins.
- **Hook caveat:** don't launch hooks through `uv run`, because it adds startup overhead to every tool call. Call the venv's Python directly and load heavy imports lazily.

## 3. MCP vs. markdown: a correction

Markdown directives to the agent are **skills**. MCP is a running server that exposes typed tools.

Recommended shape: a Claude Code plugin made of skills (markdown), hooks, and a Python MCP server (FastMCP, launched via `uvx`). That server wraps the same CLI. Codex also supports both MCP and skills.

The rubric, GitHub sync and viewer each become separately installable packages.

## 4. Can GitHub links survive rebases and deleted branches?

| Link form | What happens |
|---|---|
| `blob/<branch>/path` | Always shows the latest version, but breaks when the branch is deleted. |
| `blob/<sha>/path` | Permanent only while the commit stays reachable. A rebase or squash orphans it. GitHub keeps `refs/pull/N/head`, so commits pushed to a PR usually survive branch deletion. Commits replaced by a force-push are not guaranteed to survive (community evidence, not official docs). |
| Story file on the story branch | **Fails your requirement.** SHAs change on rebase, the branch link dies on delete, and every migration needs an issue rewrite. |

**Recommendation:** use a long-lived `planning` branch that only gets new commits. It is never rebased, never force-pushed and never deleted, and it holds only story data.
- The issue links to `blob/planning/stories/<id>.md`, which always resolves and always shows the latest version.
- At each state change you can also record a SHA permalink as a snapshot. It stays valid because `planning` never rewrites history.
- Abandoned stories stay there with their reason.
- Code branches never contain story files, so squashing or rebasing code doesn't matter.
- **Concurrency:** with one file per story there are no content conflicts. Worktrees push in a fetch, rebase-only-unpushed-commits, retry loop, so pushed SHAs never change.

## 5. GitHub API budget (verified live)

The Projects v2 REST endpoints exist and work on the REST budget, which is separate from GraphQL. I listed project #11's fields and items through REST.

Issue bodies, comments and labels are REST too. REST field writes on project items (PATCH) are only documented by third parties; I haven't tested them live. Sparse sync at state changes over REST should bring GraphQL use close to zero.

## 6. Story file format

- YAML frontmatter shows as a table in GitHub's file viewer.
- Inside `<details>`, a fenced JSON block needs a blank line after `</summary>` or GitHub won't render it.
- **Risk:** if the agent edits embedded JSON inside markdown and the code parses it back, you rebuild today's marker-loss problem.
- **Recommendation:**
  - Keep an append-only `events.jsonl` per story. It merges cleanly in git.
  - Keep frontmatter plus the prose body as the parts that get edited.
  - Have the code *generate* the `<details>` JSON blocks, and never parse them back.

## 7. Estimation and ML

Your existing #1821 design (Refine/Plan/Close record per story, a rebuildable index, calibration only from complete records) carries over almost directly.

- **Realistic ML:** the corpus is small and its features are inconsistent. Start with similar past stories (k-nearest-neighbour), with each story's features stored in a compact format, plus quantile regression for estimates.
- The "learn to plan better" part is mostly the agent pulling in lessons from comparable past stories. Numeric calibration is the narrower ML part.
- **Outcomes to record:** defects after acceptance, overruns past 4 hours, discovered work, loop-backs to Develop, and actual engaged time. Consider tokens/cost as a measure alongside hours.
- About 1,440 completed issues could be mined once into the new corpus. Their timing logs live in comments, so reading them through REST is cheap.

## 8. Viewer

The repo is public, so GitHub Pages is free. A GitHub Action builds JSON from the `planning` branch, and a static frontend shows:
- a board view
- story detail pages
- flow charts: cumulative flow, cycle time per state, and the paths stories take between states, including loop-backs

Locally it's the same static build. Another option worth discussing: Datasette-Lite, which runs in the browser via Pyodide.

## 9. Carry over vs. drop

- **Keep:**
  - the states (Backlog → Refine → Ready for Plan → Plan → Develop → Test → Review → Done)
  - entry/exit guards as a concept
  - a worktree per story
  - `[#N]` commit tokens
  - the project field schema
- **Drop:** issue-body-as-database, HTML markers, mutator locks, fences, sagas, and rewriting the timing-log comment. Aim for about 8–10 guards in total instead of 49.
- **Biggest risk:** the second-system effect, meaning the same urge to over-govern comes back. Set an explicit size/complexity budget for the new repo, and don't let it govern its own development until the core is stable.

## Open questions before we brainstorm

Reply with numbers.

1. Should story data live only on `planning` (my recommendation), or also be merged into trunk? Regular merges add a lot of data commits to trunk history.
2. Which is canonical: one markdown file with embedded JSON, or `events.jsonl` plus a generated markdown view?
3. When you edit on GitHub (drag a card, change a label), should the next sync import that or overwrite it?
4. Which harnesses: Claude Code only, or also Codex (there are existing adapters for Codex and Grok)?
5. Should the history of the 2,165 issues be imported to seed the estimation corpus?

Sources:
- [Is a deleted branch on GitHub guaranteed to not leak data? #70144](https://www.Github.com/orgs/community/discussions/70144)
- [Scaling Git's garbage collection](https://github.blog/engineering/scaling-gits-garbage-collection/)
- [GitHub REST rate limit](https://docs.github.com/en/rest/rate-limit/rate-limit)
- [GitHub Projects REST fields](https://docs.github.com/en/rest/projects/fields)
- [Projects v2 API reference (third-party)](https://glama.ai/mcp/servers/@kunwarVivek/mcp-github-project-manager/blob/1672d4e081bb23661ca959491a2f1873a5b36bd0/.planning/research/GITHUB-PROJECTS-API.md)

## User

New repo

## Assistant

I'll need a few details first, because creating the repo and its first story is visible on GitHub:

1. **Repo name and owner:** `kburson/<name>`? Some ideas: `aitm-py`, `storyflow`, `aitm2`.
2. **Local path:** `/Users/kpburson/projects/Vibe-Coding/<name>`, next to the current repo?
3. **Visibility:** Public is needed for free GitHub Pages hosting of the viewer. Private Pages requires a paid plan.
4. **License:** keep the current AGPL-3.0 plus commercial dual license?
5. **The brainstorm story:** the new tooling doesn't exist yet, so how should we track it?
   - (a) a plain GitHub issue in the new repo, with the brainstorm output committed as `docs/brainstorm.md`
   - (b) a hand-written story file in the new format under `stories/`, so we test the format early. I recommend this one, with a matching issue linked to it.
6. **Should I run `gh repo create` and the initial commit, or will you create the repo yourself?**

The five open questions from my last message (planning-only branch, which file is canonical, GitHub-edit precedence, which harnesses, importing history) are still open. We can answer them in the brainstorm itself, or you can reply to them now.

## User

to answer questions in #2 about python:

Yes, I need to learn python, it seems to be a common requirement for most AI jobs.
For this suite of agent tools we might find an optimal combination of nodejs and python, and I want to look into using typescript instead of ecmascript.  There are native runners for typescript code that run on nodejs, or we could transpile it during the package and deployment.  We could use Python for the detail scripts and nodejs/typescript for the higher level hooks and orchestration...  this is a hybridization that should be looked into, but I do want to investigate using python heavily so I can learn and demonstrate it.

## Assistant

That's a fair reason to use Python heavily. But I'd split by deployable product, not by layer as you sketched it.

**Why not TypeScript for hooks and orchestration, Python for the detail scripts:**
- Hooks run on every tool call and need to read story state. If the hook is TypeScript and the state logic is Python, every call starts two processes (Node, then Python), roughly doubling hook latency.
- The alternative is duplicating the state logic in both languages, which is how drift starts.
- Orchestration is driven by the agent, so it's slow anyway. TypeScript buys nothing there.
- Two runtimes, two package managers, two test frameworks and a cross-language interface, all inside the core. That's the same kind of weight you're trying to escape.

**Recommended split:**

| Part | Language | Why |
|---|---|---|
| Core: state machine, story store, `planning`-branch writer, GitHub sync, CLI, MCP server, hooks | Python | One runtime, no process hops; hooks read local state directly. This is the main learning and showcase surface. |
| Estimation rubric / ML plugin | Python | scikit-learn and the other ML libraries; separately installable through entry points. |
| Story viewer web app | TypeScript | It runs in the browser, so it has to be JS/TS anyway. It's a self-contained place to learn TypeScript. |
| Shared data format | JSON Schema generated from the Python data models (Pydantic), with TypeScript types generated from it | One source of truth, so the two languages can't drift. |

**What installing looks like:**
- People who use the tool need only `uv`, `git` and `gh`. No Node.
- The viewer ships as a prebuilt static site. Python's built-in server can serve it locally, and it deploys to Pages online.
- Node and TypeScript are needed only to build the viewer, in CI or your own dev setup.

**About running TypeScript natively on Node:** Node 24 runs `.ts` files directly by stripping the types. That only works for syntax that can simply be erased: no `enum`, no `namespace`, no parameter properties, and no type checking at run time (you still run `tsc --noEmit` in CI). For the viewer you'd use a bundler such as Vite anyway, so this mostly doesn't matter.

**When to revisit:** only if some part truly needs a Node-only library. The Claude Agent SDK and the MCP SDK both have Python versions, so I don't see one today.

**One thing to measure early:** how long a Python hook takes to start with its real imports. Aim for under 100ms per tool call by keeping the hook module's imports minimal.

The repo setup questions (name, path, visibility, license, story format, who runs `gh repo create`) are still waiting before I create anything.

## User

>The Claude Agent SDK and the MCP SDK both have Python versions, s

We need to maintain compatibility with both Codex and Grok...  This tool suite should be able to be run from any of the frontier labs agent stacks or harness

## Assistant

Understood. I'll take back the Agent SDK point: the core shouldn't depend on any lab's SDK or call a model at all. The harness is the agent, and the tool suite is what it calls. That doesn't change the language choice (Python core, TypeScript viewer), but it does set four layers, each portable to a different degree:

| Layer | Portability | Design |
|---|---|---|
| **CLI** (Python) | Works anywhere an agent can run shell commands | This is the guaranteed floor. All state-machine enforcement lives here: the CLI itself refuses invalid transitions. |
| **MCP server** | Claude Code and Codex support it. Grok: **unsure**, I need to verify. Your current Grok adapter doesn't use MCP. | A thin typed-tool layer over the same functions the CLI uses. Optional, never required. |
| **Skills** (`SKILL.md`) | Claude, Codex (`.agents/skills`) and Grok (`.grok/skills`) all read the same format, as your current adapters show | One shared skill plus a short shim per harness, the same pattern you have now. |
| **Hooks** | Least portable: each harness has its own payload format, settings file, trust model, session-ID variable and transcript location | One Python hook entry point, with a small translator per harness on the way in and on the way out. This replaces `grok-wire.mjs`. |

Rules that follow from this:

1. **Hooks must never be required for correctness.** They can block a bad action early or record timing, but if a hook is missing, untrusted, or fires twice (Grok can run its own hooks and the Claude-compatible ones), the CLI still enforces the workflow. That also removes much of today's duplicate-firing and fail-closed handling.
2. **Each harness's quirks live in its translator:** session ID (`GROK_SESSION_ID`, etc.), transcript path, and its own way of denying an action. The core only ever sees one common event format.
3. **Test the translators against recorded real hook payloads** from each harness, so a harness update that changes its format shows up as a failing test.
4. **Install stays one command:** `uvx aitm install --agent claude,codex,grok` writes each harness's files, as `npx ai-task-manager install` does today.
5. **Word counting from transcripts** depends on each harness's transcript format. Treat it as an optional per-harness feature, not a core requirement.

The repo setup questions from earlier (name, path, visibility, license, story format, who runs `gh repo create`) still need your answers before I create anything.

## User

new repo has been created: `git@github.com:kburson/aitm.git`

## Assistant

I've cloned the new repo to `/Users/kpburson/projects/Vibe-Coding/aitm`. If you'd rather skip the questions and have me go straight to a written design, just say so.

Walk me through the last story that got stuck in the current tool: what happened from the moment you picked it up to the point where it stalled?

## User

simply track the difficulty in getting epic 2039 to done...  The originally planned, decomposed and hydrated children expanded.  There were numerous defects found at each step, we had to further decompose children.  Right now we are trying to close up 2169 so we can close 2071 (that is almost 100 defects in between stories - much are for the prior children of 2039, but this is indicative of an epic that should take 2-3 days and has expanded to over a month.

And we have 5 more stories that are in Plan stage that I forbade the agent from starting until 2071 was closed.  I do not like extended WIP.  Start a story and finish it before you start the next;  if you must have a defect discovered during implementation then keep it to a single defect no more than 4 agent hours.  If that defect finds more defects or expands beyond the time limit then planning failed and we need to stop and return to the planning phase, find out what went wrong, get a better plan that we can execute successfully, not grope around in the dark ever expanding scope until nothing gets done and we have distributed spaghetti code.

## Assistant

Here's what I've got so far about the core of the new tool: the delivery discipline it enforces.

**What you said**
- **Finish before starting.** A story gets finished before the next one starts. No long-lived WIP.
- **Defect budget.** During implementation, at most one discovered defect, sized at 4 agent-hours or less.
- **Planning-failure stop.** If that defect turns up another defect, or runs past 4 hours, the plan has failed. Work stops and the story goes back to Plan. There you find out what the plan missed and produce a better plan that can be executed, instead of letting scope grow.
- **The failure you're designing against:** epic #2039 was planned at 2–3 days and is now over a month. Children expanded and were decomposed again, with close to 100 defects in between. Five stories sit in Plan, held back on purpose.

**What that means for the design (my reading)**
- Today's rule (file the defect, mark the parent blocked, drive the chain deepest-first) makes unbounded defect chains legitimate. The new tool reverses that: a second defect isn't a new blocker to chase. It is a stop signal, and the CLI refuses to start it.
- Each stop is a recorded event: what was planned, what was found, and why the plan missed it. These events are the most valuable training data for the planning rubric. They're the "learn from every story" signal you described.

**My guesses (correct me)**
- The WIP limit is one active story per project, not one per agent or worktree.
- Epics get the same treatment: an epic that runs well past its planned total trips the same return to planning.
- When a story goes back to Plan, the code already written stays parked on its branch. It isn't merged, and the new plan decides whether to reuse or discard it.
- The 4-hour cap applies both to every leaf story at planning time and to the defect, so one number governs both.

What's wrong or missing in that?

## User

WIP limit allows for parallel stories.  We look to optimize calendar time by using parallel agents working on separate, independent stories.  Each of these stories should limit their WIP expansion to a single defect or discovered story.  If that agent's story expands beyond those limits then it did not plan the implementation well in the JIT planning (deep-dive).  I would prefer the system learn from the mistakes and determine to scrap and start over or refactor and improve.

## Assistant

Updated:

**WIP is per story, not per project.** Several agents can work in parallel to save calendar time, each on its own independent story in its own worktree. The limit is on *expansion*: each story may absorb one defect *or* one discovered story, and no more.

**A trip means the deep-dive failed.** If a story goes past that allowance, the just-in-time implementation plan (the deep-dive) missed something. That's the planning failure to learn from, rather than the earlier Refine-level breakdown.

**On a trip, the system chooses between two recoveries:**
- **Scrap and restart:** throw away the branch and re-plan from scratch.
- **Refactor and improve:** keep the code, re-plan the remainder, and fix what's there.

Over time the system should learn which choice fits which situation. That means recording the decision, its reasons, and how the restarted or refactored story turned out.

**My guesses (correct me)**
- Stories are judged "independent" at planning time, mostly by not touching the same files or modules. Parallel agents don't coordinate with each other while they work.
- The allowance is one expansion in total: a defect *or* a discovered story, not one of each.
- When one story trips, the stories running beside it keep going. Only the tripped story stops.
- At first the agent *recommends* scrap or refactor with its evidence and you approve. As the record shows its calls turn out well, it earns the right to decide alone.

What's wrong or missing in that?

## User

<!-- attach -->
> The allowance is one expansion in total: a defect or a discovered story, not one of each.

no.  The expansion is per recorded story; thus a defect that was expanded from a story counts as that story's single expansion.  Other agents working on other stories will have their own expansion threshold.

## Assistant

Got it. I'll record the rule as follows:

- **Each recorded story has its own expansion count, and the limit is one.** Whatever the story spawns, whether a defect or a discovered story, uses that one slot. Another agent's story has its own separate count, so nothing is shared across parallel work.
- **What the story spawns gets no slot of its own** (my reading of "if that defect finds more defects… planning failed"). The chain can be at most one level deep. If the spawned defect expands, the *parent* story has tripped, because the parent's deep-dive is what missed it.

Looking six weeks ahead at the new repo, what would make you wince?

## User

A fully planned epic with a hydrated decomposition of child stories with a few already completed then we get blocked and cannot close a current story because of some rule that was skipped by the agent -- they forgot to record the correct receipt or they recorded the timing log badly and it requires someone to fix their mistake.  This angers me above all -- the agent making mistakes on key stepping stones for any story, they we have to go back and fix them.  Or the agent decides it cannot move forward with the planned scope without fixing a defect elsewhere in the code -- this is indicative of poor planning and poor execution on multiple levels.  This is the roller coaster that I ride today while attempting to close up 2039 and get back to all the defects < 2000; but I cannot even get to those defects because we have layered defects from 2000 to 2171.  It seems an endless train of defect stories -- hence I am considering a full rewrite to assimilate lessons learned from the original.

## Assistant

I'll play this back as the anti-goals: what must never happen.

**1. Bookkeeping must never block delivery.**
- Today the agent has to remember to record receipts, timing rows and markers. When it forgets or gets one wrong, a story can't close until someone repairs the record.
- In the new design, my reading is that the agent never records bookkeeping by hand. The tool records it as a side effect of the commands it already runs. For example, `aitm test` runs the tests and writes the receipt itself, and timing comes from the events the tool itself records, not from rows the agent writes. The agent can't forget a step it doesn't perform.
- If a record is missing or damaged anyway, the tool rebuilds it from git history and the event log. A gap in the paperwork is never a close-blocker that only a person can fix.
- Real quality gates stay: tests must pass, and review must happen. The tool produces that evidence itself instead of asking the agent to prove it.

**2. Scope never reaches outside the plan mid-flight.** If an agent finds it can't continue without fixing code elsewhere, the deep-dive missed something. That's a trip back to planning, not permission to wander. We already have this rule.

**3. The tool's own defects must not take over the backlog.**
- Today, defects #2000–#2171 are mostly the tool fixing itself. They stand between you and the real backlog below #2000.
- My guess: part of the cause is that the tool governs its own development, so every bug in the tool blocks work on the tool. The new repo should stay out of its own governance until the core is stable, then adopt itself deliberately.

**The one-line anti-goal:** the tool must never be the reason a story can't close.

What's wrong or missing in that?

## User

>The native test caught another projection call that was missing the validated authority. I’ve connected it within the planned Close file and restarted the end-to-end test.

This is from the latest work by CODEX agent working on 2169

with these to follow:

>The native test found a second part of the same Close bug: Close writes its required terminal timing rows, then its next waiver check treats those rows as erasing the earlier “waived” result. I’m reviewing a Close-specific way to preserve that evidence while still revalidating the waiver and retaining the timing rows.

>The Close-specific timing reader passes its tests, and Deliver still rejects a wrapped handoff. The native test is now checking valid closure plus missing, expired, revoked, wrong-source, wrong-requirement, and stale-scope waiver refusals.

>The next failure is also in that authority read: it counts an estimation record containing a copied timing snapshot as a second timing log. I’m aligning its selection with the existing canonical timing-heading rule. Two genuine timing logs will still cause a refusal.

---

All of this is a failure of the agent to either plan or implement correctly, and I pay the price in tokens, limits and calendar time.

## Assistant

This is useful evidence. Here's what I read in it.

**All three bugs come from the same cause.** One file of text is written by several parts of the tool and then read back by guessing at its shape:
- Close writes its timing rows, and the waiver check then reads those rows as cancelling the earlier "waived" result. Two kinds of fact share one surface, and their order changes their meaning.
- An estimation record contains a *copy* of the timing data, and a reader takes the copy for a second, real timing log. The reader decides what something is from its heading, not from what it actually is.
- A projection call was missing its validated authority. That's one more piece of hand-wired plumbing that every caller must remember.

**My honest assessment:** the agent's planning is weak, but this design also makes good planning nearly impossible. Any change to Close touches timing, waivers, estimation and projection at once, through rules that live only in regexes. No deep-dive can hold all of that, so plans fail one bug at a time. And your 4-hour trip rule would have stopped #2169 long ago.

**Design rules this suggests for the rewrite:**
1. **Each fact has exactly one writer and one home.** Timing events, waivers and estimates live in separate typed records, never mixed into one text surface.
2. **Readers never recognise data by its shape.** Records carry an explicit type and a schema. A copy is labelled as a copy, or it's a reference instead of a copy.
3. **Events are appended, never rewritten,** and current state is calculated from them. A later event can't erase an earlier one by accident, because nothing is overwritten.
4. **The story's markdown is generated output.** Nothing parses it back for decisions.
5. **Few rules, each in one place.** Wiring like "this call needs authority" is enforced once, centrally, not by each caller.

What's wrong or missing in that?

## User

This aligns with my idea to have a local data store for story development; we can separate the different data into different files, organize them in a folder tree, use a sqllite db to track files and changes etc (although that requires the db file to be committed into git history, which has it's own challenges with concurrent activity -- hence a custom data store of files in a hidden folder structure is probably better.

Using a datastore that can handle rapid CRUD operations  ( without requiring a hosted DBMS that costs money and can transport with the git clone|origin ) will allow the internal systems to manage the data more efficiently; but, we will need an ability to make all of this human accessible thru the story management web app.

## Assistant

Here's how I'd put the datastore together.

**Files are the authority. SQLite is only a fast index.**
- Story data lives as many small files in a hidden folder tree, for example `.aitm/stories/<id>/`. Each kind of data gets its own file: `story.md`, `events.jsonl`, `estimate.json`, `tests.jsonl`, and so on.
- Those files are committed to git, travel with every clone, and need no hosted database.
- A SQLite file is built *from* those files on each machine and is gitignored. It is never committed, so concurrent work never runs into conflicting database files. If it goes missing or stale, it is rebuilt. Fast reads and queries come from the index; writes go to the files, and the index updates as they're written.
- GitHub's file viewer shows dot-folders normally, so story links from issues still work.

**Writing to the `planning` branch from any worktree** (my proposal):
- Agents work on story branches in their own worktrees, but story data belongs on `planning`.
- Git can commit to a branch without checking it out: it writes the file objects, builds the commit, then moves the branch pointer only if it hasn't changed since it was read.
- Parallel agents can each commit their own story's files straight to `planning`. If two arrive at once, one retries. No shared checkout, no lock files, and story branches never carry story data, so rebases don't matter.
- **The catch:** `planning` must never be checked out as a working tree, or that tree goes out of sync. This is the trunk `update-ref` problem you've already hit.
- Each event is committed locally right away. Pushes to origin are sparse: at state changes, plus pulls before reads that need fresh data.

**The web app** reads the same files.
- Online: a GitHub Action builds JSON from `planning` and publishes it to Pages.
- Locally: it reads the SQLite index for live data while agents work.

**Open point (my guess):** agents running in the cloud or on another machine follow the same rules and sync `planning` through origin. Conflicts are rare because each story's files have one writer.

What's wrong or missing in that?

## User

If we use "planning" as a sister branch to the default (trunk) then we will need to protect that branch so it cannot be deleted.  That means the git repo will have 2 parallel managed branches, the default branch and the planning branch.  The planning branch is where all the story planning and tracking data is held, the default branch is where deployable story implementation is held.  Both branches block delete or rebase or any other form or history rewrite without an explicitly authorized user...  We need to be able to secure the planning data as much as the implementation.  This does imply that a 2 repo solution might work better, one for ARD and tracking with the other for implementation, but that requires more cost and effort in maintaining the dual origin product structure.  Do I have this correct?

Also, side note: The `.aitm/story` sub tree of folders should not get too deep or too wide, meaning we need to limit the number of folders deep, but we also do not want file sprawl in a single folder causing hundreds of unrelated files in a single folder becomes a "needle in a haystack" search and recovery challenge, both for the user and the agent.  We need to optimize that folder and file structure

## Assistant

Mostly yes. Here's the corrected picture.

**Two protected sister branches**
- GitHub rulesets can protect `trunk` and `planning` against deletion and force-push, with you on the bypass list. They're free on public repos.
- The two branches get *different* rules:
  - `trunk`: no deletion, no force-push, changes only through a PR.
  - `planning`: no deletion, no force-push, but **no PR requirement**. Agents push fast-forward commits to it directly. Requiring PRs there would bring back the overhead we're removing.
- This settles the earlier open question: `planning` is **never merged into trunk**. They're parallel histories with separate jobs.

**Two branches vs. two repos**

| | One repo, two branches | Two repos |
|---|---|---|
| Setup and auth | One clone, one remote, one token | Two of each |
| Issue to story-file links | Same repo | Cross-repo (works, but adds config) |
| Separate permissions | No: same access to both | Yes: for example, code public and planning private |
| Pages / viewer | One site | Pick one repo to host it |

My recommendation is one repo with two branches now. The store location (remote plus branch) should be a config value, so moving to a separate repo later is a config change, not a rewrite. The only strong reason to choose two repos is wanting different visibility for planning data and code.

**Folder layout: paths computed from the story ID, never from meaning**
```
.aitm/stories/020/2039/story.md
                     events.jsonl
                     estimate.json
                     attachments/
```
- The bucket is the ID divided by 100, zero-padded. That gives at most 100 entries per folder and a fixed depth of three levels, and it works up to 99,999 stories.
- **The path can be computed from the ID alone,** so the agent never searches. That's the fix for the needle-in-a-haystack problem.
- Paths are never grouped by epic or by state, because re-parenting or a state change would move the file and break the GitHub link. Epic membership and state go in frontmatter and the index.
- Each story folder holds a small fixed set of known file names. Anything extra goes in `attachments/`.
- Done and abandoned stories stay where they are, so links never break.

**Open point:** a story drafted locally has no GitHub issue number yet. Either create the issue up front (one cheap REST call), or keep drafts in `.aitm/drafts/` and move each one once at publish, before any link to it exists.

What's wrong or missing in that?

## User

I like keeping draft stories that are not yet entered into the product backlog in a separate `.aitm/drafts/` folder. This will be used during planning, and if the plan is discarded before we create a story id in github to record the PBI (Product Backlog Item) then we can simply delete that draft subfolder.  We would need a manner to index the draft subfolders, either a monotonically increasing index, timestamp and word description of the story idea.

I would like to expand this idea to use the drafts for brainstorming ideas and have those ideas farmable | mineable during any planning session.

## Assistant

Here's how drafts and ideas would work.

**Naming draft folders**
- A counter that only goes up breaks under parallel work: two agents, or two machines, both create "draft 42". Keeping one shared counter safe brings back the coordination we're removing.
- Instead, use a timestamp plus a short description, which sorts correctly and doesn't collide in practice:
  `.aitm/drafts/2026-11/20261108-1530-local-backlog-store/`
- Folders are grouped by month to keep `drafts/` from getting wide, the same idea as the ID buckets.
- If two drafts with the same description land in the same minute, the second gets a two-character suffix.

**Ideas and drafts are one pool, at different stages**
- **Idea:** one short file holding the thought, why it matters, and tags. Capturing one is a single command, `aitm idea "..."`, quick enough to use mid-conversation like this one.
- **Draft:** an idea grown into a shaped story or epic: scope, acceptance criteria, rough size.
- **Published:** it gets a GitHub issue number and moves to `stories/<bucket>/<id>/`. The story's frontmatter records `origin: drafts/2026-11/...`, so learning can trace an idea all the way to its outcome.
- **Discarded:** the folder is deleted. That's safe because `planning` keeps the deletion in its history.

**Making ideas mineable**
- The local index covers ideas and drafts as well as stories. A planning session can query them by tags, keywords, and the areas of code they touch, and pull related ideas into the plan.
- Mining discarded ideas by walking git history would be slow. My proposal: discarding also appends one line to `.aitm/drafts/discarded.jsonl` with the title, reason, and the commit SHA where the folder last existed. The folder still goes away, but the idea stays findable, and "we already tried and rejected this" becomes something planning can learn from.

What's wrong or missing in that?

## User

I want to include the superpowers design and plan documents in the planning:`.aitm/stories/{story-id}/{design|plan}/` folders along with all review collateral.  This is a better place to store this data than in the default branch mixed with the story implementation code.

## Assistant

Agreed. That gives each story folder this shape (keeping the ID bucket):

```
.aitm/stories/020/2039/
  story.md  events.jsonl  estimate.json
  design/   spec.md   reviews/20261108-codex-r1.md
  plan/     plan.md   reviews/20261109-claude-r1.md
  attachments/
```

**What follows from this**
- **No version-numbered files.** Revisions are just new commits on `planning`. Each review records the commit SHA of the design or plan it reviewed. Because `planning` is never rewritten, that link to "exactly what was reviewed" stays valid for good.
- **Drafts use the same layout.** A draft's design and plan travel with it into `stories/` when it's published.
- **Trunk holds only code.** Commits and PRs link to the story's design and plan on `planning` instead of carrying them.
- **Superpowers needs redirecting.** Its brainstorming and planning skills save to `docs/superpowers/` in the current checkout. The aitm skill has to tell them to save into the story folder instead.

**One problem this exposes**

Agents edit files with ordinary file tools inside their story worktree, but `planning` is never checked out anywhere. My proposal:
- On story branches, `.aitm/` is gitignored.
- When an agent binds to story 2039, aitm copies that story's folder from `planning` into the worktree's `.aitm/`.
- The agent reads and edits those files normally.
- `aitm sync` (and every state change) commits the changes back to `planning` without a checkout, as described earlier.
- Only that story's folder is ever written from that worktree, so there's one writer per story and no conflicts.
- The rest of `planning` stays readable through the index, for mining comparable stories and ideas.

Does the copy-in, sync-back model fit how you picture agents working on a story's design and plan?

## User

I want to investigate creating specialized design and plan agents for generating these documents, including any research and analysis on current code base and current industry trends or patterns.  Will customized agents be better than simply using the harness agents with the superpowers design | plan skills ?

## Assistant

Specialized agents should do better, but not because their instructions are better than superpowers'. The gains come from four structural things a skill can't give you.

**What specialized agents add**
1. **Separate context.** Research on the codebase and the web runs in its own context and returns a summary. The main session doesn't fill up with file dumps.
2. **Tool limits enforce the rules.** A design or plan agent that can't edit code *can't* start implementing before the plan is approved. That turns a rule agents keep breaking into one they can't break.
3. **Inputs fed in automatically.** aitm can hand the planning agent a compact packet every time: comparable past stories, their trips and why they happened, and the files and dependencies involved. That makes the learning loop real instead of hoping the agent goes looking.
4. **A truly independent reviewer.** A reviewer that never saw the author's reasoning, ideally on a different model or harness (as your Claude/Codex peer review does now), checks the plan against the actual code.

**Costs**
- **Portability.** Claude Code has custom subagents. I'm **unsure** whether Codex and Grok support custom agent definitions natively. Each role should therefore be defined once in a harness-neutral form: prompt, allowed tools, inputs, output schema. aitm generates a native agent where the harness supports one, and falls back to running the skill in the main session where it doesn't.
- **Cold start.** Each spawn starts from nothing, which costs tokens. The context packet keeps that small.
- **Don't rebuild superpowers.** The agents should *use* the brainstorming and writing-plans skills, with aitm adding the inputs and the output requirements.

**My recommendation:** three roles, no more.
- **Researcher:** read-only, cheaper model.
- **Planner:** writes only to the story's `design/` and `plan/` folders.
- **Plan reviewer:** independent.

The plan output has a fixed schema: each leaf story at 4 hours or less, the files it touches, risks, and likely defect areas. A plan that misses the schema is rejected automatically.

Industry-trend research is expensive and rarely pays off for an individual story. I'd make it opt-in for epics only.

Whether this is actually better gets measured: the trip rate before and after, from the same data that feeds the rubric.

Where do you think 2039's planning first went wrong?

## User

<!-- attach -->
> Drafts use the same layout. A draft’s design and plan travel with it into stories/ when it’s published.

no...  drafts are for brainstorming before the design.  Ideas are parking lots before drafting.

Once a draft is ready to graduate to a story it is first given a github story id, then all collateral moves to that proper story folder, and then the designs and plans can be generated and reviewed.

## Assistant

Corrected lifecycle:

1. **Idea:** a parking lot. One small file, captured quickly, mined later.
2. **Draft:** brainstorming. The idea gets shaped into a candidate story or epic. There's no design or plan yet.
3. **Graduation:** the draft gets a GitHub issue number, and its collateral moves to `.aitm/stories/<bucket>/<id>/`. This is the point where it joins the product backlog.
4. **Design:** written and reviewed inside the story folder.
5. **Plan:** written and reviewed inside the story folder.

So `design/` and `plan/` exist only under `stories/`, and every design has an issue to link to. A discarded draft never touches GitHub. Brainstorm output (this conversation would count) is draft collateral that moves with the draft when it graduates.

Walk me through what should happen to a story between graduating to the backlog and an agent starting to write code.

## User

when a story moves from draft to story that means that brainstorming has collected all the data necessary to produce a story description and a design document. next:

1. create github issue id for the drafted story.
2. create the story storage location and move the draft markdown file.
3. generate the story body with basics

       a. story form "as a develop I want..."
       b. scope
       c. metadata
              i. story origin
              ii. draft document path
              iii. creation date
       d. dependencies [ parent issue, is blocking, blocked by]

This should be enough for the github story to describe the task|defect|feature, it is now ready for a design.

4. generate design document for the story scope and description

5. execute multiple levels of review ( SAR, SPR, XPR ) using ai-peer-review.  The peer-review tool should be configured to use the target folder for storing review collateral.  This will require a refactor of the peer-review tool to allow a custom location for every review session.
6. the story is now ready for refinement.  This is where the story design feeds into an estimate for the amount of agent engagement is required to complete the story, the size, original estimate and priority for the story.
7. moving to plan the design is converted to an implementation plan
8. execute multiple levels of review on the plan until final acceptance.  This should not require human review. All collateral is stored similar to the design review.
9. Epic/Story estimates are revised according to the plan.
10. The story then needs a JIT implementation plan, which can simply accept the accepted plan if it was just generated and reviewed, or the JIT can generate a revision on the accepted plan according to the current state of the code base.  Having the plan generated before the JIT Deep dive helps the deep dive generate quickly, even if revisions are required to keep pace with current revisions.
11. Once the JIT plan is generated / revised and the estimates are revised the story is ready for dev.


follow the established patterns in the ai-task-manager state machine.  I want to keep the flexible structure of the state machine as the 3 part state machine object

{ pre-guard, action, pre-exit-guard

## Assistant

Here's your sequence mapped onto the state machine. Each state keeps the three parts you named: entry guards, resident actions, exit guards.

| State | Work done in the state (your steps) | Exit guard: may leave when… |
|---|---|---|
| **Backlog** | 1–3: graduation creates the GitHub issue, creates the story folder, moves the draft, and generates the body (user story, scope, metadata, dependencies) | the body is complete and dependencies are recorded |
| **Design** *(my guess: a new state)* | 4–5: the design is generated, then SAR → SPR → XPR reviews run, with collateral saved to `design/reviews/` | the design is accepted by review |
| **Refine** | 6: the design feeds into the agent-engagement estimate, size, original estimate and priority | every field is set, and a leaf story is estimated at 4 hours or less (otherwise it is split) |
| **Ready for Plan** | queue | WIP and dependency checks pass |
| **Plan** | 7–9: the plan is generated, reviewed at multiple levels with no human, and the estimates revised | the plan is accepted and the estimate revised |
| **Ready for Dev** *(my guess)* | 10–11: the JIT deep-dive accepts or revises the plan against current code, and estimates are revised again | the JIT plan is recorded and the story is still within its limits |
| **Develop → Test → Review → Done** | as today | as today |

**Design rules I'd carry with this**
- **Guards are fast, local checks only.** They read the story's files and the index, with no network calls and no parsing of markdown.
- **Resident actions are idempotent setup work.** Updating GitHub is the resident action on entering a state. That *is* the sparse sync cadence: one projection per state change.
- **The deep design and planning work** is done by the specialized agents while the story sits in a state. The work lives in the state, but it isn't part of the state object.

**Dependencies outside this repo**
- ai-peer-review needs a refactor so each review session can write to a location chosen by the caller.
- My guess at the review levels: SAR = single-agent review, SPR = same-provider peer review, XPR = cross-provider review.

**My guesses**
- Design is its own state, not work done inside Backlog. That gives the design review an exit guard of its own.
- The design, like the plan, needs no human review.
- JIT sits just before Develop, because a plan can go stale while the story waits.

What's wrong or missing in that?

## User

>Design (my guess: a new state)

a Backlog item must have a design before it can move to refine.  There is nothing to refine if you do not know what you are going to build.  The "plan" is the document that defines how you are going to deliver the design.

## Assistant

Corrected. There's no Design state.

- **Backlog** contains graduation (steps 1–3) *and* design (steps 4–5).
- **Backlog's exit guard is "design accepted by review."** A story with no accepted design can't enter Refine.
- **Design means what to build. Plan means how to deliver that design.** Refine sizes the design. Plan turns it into delivery steps, and is then re-sized.

So the walk keeps today's states: Backlog → Refine → Ready for Plan → Plan → (JIT) → Develop → Test → Review → Done. Where the JIT deep-dive sits is still my guess.

Where in this flow do you still want to sign off personally?

## User

Normally after delivery.  I can watch the agent while it works, use the local story viewer to see the progress along with how long it has taken to finish the work, and any bumps in the road.  I can make suggestions along the way as I review the designs and plans.  For the most part these designs are archival records but are too long and detailed to be read casually by the user.  In practice I do not read the designs or plans and simply rely on the agents to properly review them using the peer-review tool.  I do have events where I need to question the direction or progress of the agent, and we can pivot at those points.

## Assistant

Here's your role as I understand it.

**One sign-off, after delivery.** The only required human gate is accepting the finished work, at Review → Done. Designs, plans and code reviews are all handled by agents through the peer-review tool. Nothing waits on you before delivery.

**Watching, not approving.** While work runs, the story viewer shows you:
- where the story is in the flow, and how long each stage has taken
- the bumps: defects, discovered work, extra review rounds, and trips back to planning

You step in when something looks wrong, not on a schedule.

**Designs and plans are archival records.** They're too long to read casually, so humans don't read them. My guess: the viewer shows a short generated summary of each one (what, why, main risks, estimate, review result), with the full document a click away.

**Pivots are recorded events** (my guess at the details):
- When you question the direction and the story changes course, the tool records who stepped in, why, and what changed.
- A pivot that changes scope sends the story back to Plan, but it's recorded as a *human pivot*, separate from a planning-failure trip. The rubric shouldn't blame the agent's planning for a change in your direction.
- A pivot that catches something the agents should have caught is a different case, and is also a learning signal.

**One consequence:** because you don't read designs or plans, the independent reviews are the whole safety net before delivery. The cross-provider review (XPR) matters most.

What's wrong or missing in that?

## User

<!-- attach -->
> My guess: the viewer shows a short generated summary of each one (what, why, main risks, estimate, review result), with the full document a click away.

yes, but also the user can discuss with an agent how the design, plan and implementation are in alignment, get an evaluation of what went well, what should have been planned better, what lessons were learned, and a confidence vote on moving forward.

## Assistant

Added. Here's how I'd shape it.

**An alignment and retrospective conversation about each story**, covering:
- whether the design, the plan and the implementation actually match
- what went well, and what should have been planned better
- lessons learned
- a confidence vote on moving forward

**Where the conversation runs** (my proposal):
- The viewer can't host the agent itself: the online copy is a static Pages site, and calling a model API directly would tie the tool to one lab and add cost.
- Instead, the viewer's "Discuss" button gives you a command, `aitm discuss 2039`, to run in whatever harness you use. aitm loads that harness's agent with a compact story packet: summaries, the event timeline, bumps, the code diff, and links to the full documents.
- The discussion itself happens in the harness, so it works the same on Claude, Codex or Grok.

**What gets saved**
- Each discussion produces a structured record in the story folder (`retro/`): an alignment verdict, what went well, planning misses, lessons, and the confidence vote with its reasons.
- A retro is produced automatically just before your sign-off, and on demand at any other time.
- These records feed the planning rubric. Lessons you approve in a conversation become training signal, not just chat history.

**My guess about the confidence vote:** it's advisory, a score with reasons, shown when you sign off. A low vote invites a discussion but doesn't block delivery.

What's wrong or missing in that?

## User

>Where the conversation runs (my proposal):

yes, the story viewer allows the user to view the progress of the story, along with costs and such.  The user can then start a conversation in an agent chat session about the story, using the reviewer to help visualize the conversation context.  

But an idea I had from this is that during the agent sign on of the review state the agent could produce a "retrospective" document and attach to the story that describes the basis of what the above conversation might be...  If the user wants more information they can use the story, the story visualizer and the agent sign-off documents to spark a conversation on how to improve the process.

## Assistant

Confirmed:

- **The retrospective is part of the agent's sign-off.** On entering Review, the agent writes `retro/` covering design/plan/implementation alignment, what went well, planning misses, lessons and a confidence vote. It's attached to the story and shown in the viewer.
- **Conversations are yours to start, when you want one.** The story, the viewer and the sign-off documents give the agent its starting context.
- **Running `aitm review` produces the retro itself.** The agent writes it as part of that command, not as a separate step it could forget. That keeps it on the right side of the "bookkeeping never blocks" rule.

**Sizing:** this is several projects, not one. I'd brainstorm and design them one at a time, in this order:

1. **Core:** story store (`planning` branch, ideas/drafts/stories, local index), the state machine (entry guards, resident actions, exit guards, the expansion limit and trip rule), the CLI, and the GitHub projection plus `init`. This matches the first slice you named.
2. **Harness integration:** skills, per-harness hook translators, an optional MCP server, and specialized agent roles for Claude, Codex and Grok.
3. **ai-peer-review refactor:** let each review session write to a location the caller chooses. This lives in the separate peer-review repo and is small.
4. **Story viewer:** TypeScript, local plus Pages: progress, costs, bumps, summaries, retros.
5. **Planning and estimation rubric plugin:** ML calibration, comparable stories, lessons.
6. **History import:** mine the current repo's ~2,165 issues to seed the rubric.

Projects 2 and 3 can run in parallel with 1 once the core's data format settles.

Does that order work for you?

## User

I want to look for opportunities to publish multiple smaller projects as a core and a set of plugins or extensions...  each extension in a separate repo.   A full install would have all of the extensions loaded and configured for the given repo.  Some extensions may have dependencies on other extensions, and all will have a dependency on the core.

## Assistant

Here's how a core plus extensions would work in Python.

**Packaging**
- Each extension is its own package (and its own repo, as you want) that depends on `aitm-core`. When one extension depends on another, that's an ordinary package dependency.
- Extensions register themselves through Python entry points, so the core finds whatever is installed without any hard-wired list.
- A **full install** is a meta-package, `aitm`, that depends on every extension: `uv tool install aitm`. Partial installs pick individual packages.
- Each repo declares which extensions it uses in a committed config file (my guess: `.aitm.toml` on trunk). `aitm init` installs and configures those extensions for that repo.

**What an extension can add**
- Entry guards, resident actions and exit guards for any state. For example, GitHub adds a projection action on every state entry, and the rubric adds a Refine exit guard requiring an estimate.
- CLI commands, MCP tools, skills, agent roles and hook handlers.
- Its own event types and story files, under its own namespace. **One writer per fact applies here too:** the core refuses to load two extensions that claim the same file or event type.

**Proposed split**

| Package | Depends on |
|---|---|
| `aitm-core`: store, index, state machine, CLI, extension API | none |
| `aitm-github`: issue provider, Project projection, `init` | core |
| `aitm-harness`: Claude, Codex and Grok adapters (my guess: one package, since they share the hook translator) | core |
| `aitm-agents`: researcher, planner and plan-reviewer roles | core, harness |
| `aitm-peer-review`: bridge to ai-peer-review | core |
| `aitm-rubric`: estimation and ML | core |
| `aitm-viewer`: TypeScript build plus a serve command | core |

**Issue IDs need an abstraction.** Graduation needs an issue number. Either the core defines an "issue provider" interface (GitHub first, GitLab or Jira later, plus a local-only provider for offline use), or the core requires GitHub. I recommend the interface.

**Risk to be blunt about:** splitting into separate repos *before* the extension interface stabilises means every interface change is a coordinated release across several repos. That's a new kind of weight. My recommendation:
- Start as one repo (`kburson/aitm`) with separate packages under `packages/`, built with `uv` workspaces.
- Publish each package separately from day one.
- Split into separate repos once the extension interface reaches 1.0.

What's wrong or missing in that?

## User

sounds good...  I hope to learn alot from this process.

yes, we will need to abstract the git origin access and the product backlog storage access to allow for github, gitlab, jira and maybe bitbucket cloud to interact with the remote apis of each service.  For now we will focus on github for both git and backlog (issues)

## Assistant

Two provider interfaces, then, kept separate because one service can fill one role without the other (Jira holds a backlog but no code):

**Git host provider**
- pushes and fetches `planning` and story branches
- pull requests and CI status
- branch protection rulesets
- **building file links** (each host formats blob URLs differently, so the story-file links come from here)

**Backlog provider**
- creating and updating issues: body, labels, assignee
- parent/child links and dependencies (blocking, blocked by)
- **the board projection:** state, priority, size, estimate, time fields. GitHub Projects, a Jira board and GitLab issue boards each implement this their own way.
- `init`: creating and configuring the board for a repo

GitHub fills both roles first, through REST where it can and GraphQL only where REST can't do the job. GitLab, Jira and Bitbucket Cloud come later as extensions that implement the same interfaces. The core never imports anything GitHub-specific.

How do you picture yourself learning Python through this build?

## User

during development I will as agents to describe the code to me and perhaps create a tutorial for me using this project code.  It is always more powerful to learn a language and it's libraries on a real project than on sample projects like todo list keepers or other things you have no interest in.  If I can learn how and why we build what I want built -- I can learn the best uses for the language and libraries.

## Assistant

That fits the design. Here's how I'd build learning in:

- **Clear code over clever code.** Modern Python (3.13), type hints everywhere, small modules, and standard libraries widely used in AI and backend jobs: Pydantic for data models, Typer for the CLI, httpx for HTTP, pytest for tests, Ruff for linting, scikit-learn later for the rubric. You'll be learning the stack employers actually ask for.
- **Every library choice comes with a short "why this over that" record.** That doubles as tutorial material.
- **Tutorials built from the real code,** in `docs/learn/` on trunk, one per milestone. Each walks through the code that was just built, the Python features it uses, and why.
- **My guess:** each story's retro gets a short "Python concepts introduced" section, so tutorial topics pile up as a side effect of normal work.

I think we've covered enough to write the design. It would be an architecture overview, covering the lifecycle, data store, packages, providers and harnesses, plus a full design for project 1, the core. A reviewer agent reads it before I hand it to you, so I may come back once with a few questions.

Should I write it into a hand-built `planning` branch using the story folder layout, or as a plain doc on trunk for now?

## User

let's start with the planning branch, keeping the 2 base branches separate from the start.

We will need to discuss ongoing development -- once we have a core in place will we dogfood the core to we can see the problems in action as we develop, or will we keep the workspace clear of the implemented rules; this latter action would require a separate project for testing the tools in real life situations, that would cost more tokens and time and not sure what we would use them on, except for possibly the extensions, or the ai-peer-review, or possibly a re-write of the ai-peer-review using the upgraded stack...  That would give us a few isolated repos to install the core and any completed extensions without having to constipate the development process of the core or specific extensions...  This is a complex question to answer, which is better.  I feel if we can do this efficiently and dogfood along the way then we should, bit I feel it is that "dogfooding" too early that has blocked the main ai-task-manager project from progressing.

## Assistant

**Planning branch:** agreed. `trunk` and `planning` stay separate from the first commit.

**Dogfooding:** my recommendation is to dogfood the record-keeping, but not the enforcement, inside the core repo.

What blocked ai-task-manager wasn't dogfooding itself. It was dogfooding with enforcement switched on. A bug in Close stopped you closing the story that fixes Close, so the tool locked itself out. Every defect in a gate became a blocker on the fix for that gate, and that's the defect chain you're living in.

So, three tiers:

1. **The core repo runs in advisory mode.**
   - Stories, events, timing, retros and the viewer all run on the core's own work from early on, so you see real data and real problems quickly.
   - Guards *report* instead of *refusing*. A tool bug becomes a recorded event, never a blocker, and the core can never lock itself out.
   - Enforcement on the core repo switches on only after the core has been stable on outside projects.
2. **Extension repos run with enforcement on.** They're real work you actually want, not demo projects:
   - the ai-peer-review rewrite on the new stack, which also covers project 3
   - the GitHub extension
   - the viewer
   
   They're where the rules prove themselves under real conditions, at no extra cost, because that work has to happen anyway.
3. **Those consumer repos install released versions of the core,** not live trunk. A broken core trunk can't block them, and upgrades are deliberate.

The cost is a slower feedback loop on enforcement bugs, which only show up in the extension repos. I think that's a good trade: it's the exact failure mode that sank the current repo.

**Writing the design means following the lifecycle by hand:**
1. Save this brainstorm as a draft.
2. Create issue #1 in `kburson/aitm`, an epic, "aitm core: story store, state machine, GitHub projection".
3. Move the draft into `.aitm/stories/000/1/`.
4. Write the design into its `design/` folder.
5. Push the `planning` branch.

May I create issue #1 in `kburson/aitm` and push the `planning` branch?

## User

I feel that we will need a master plan with sub-plans for each section (core, viewer, extensions etc)

## Assistant

Agreed. Here's how that fits the lifecycle we just defined.

**Master level: issue #1, the root epic, "aitm product"**
- `design/`: the architecture overview. It holds the cross-cutting decisions: lifecycle and states, the expansion limit and trip rule, the data store and `planning` branch, the providers, packages and extensions, the harnesses, human sign-off and retros, advisory-mode dogfooding.
- `plan/`: the master plan. It sets the order of the sections, how they depend on each other, which repo each lives in, and when the core switches from advisory to enforcing.

**Sections: child epics, each with its own design and plan**
- core, GitHub extension, harness, agents, peer-review rewrite, viewer, rubric, history import
- Each section's design and plan are written **when that section comes up**, not all now. A design written months ahead goes stale, and doing them all at once would be extended WIP at the planning level.
- **Only the core graduates now** (issue #2). It's the only section we've brainstormed enough to describe and design. The others start as drafts in `.aitm/drafts/` with what we've said so far, and each gets its own brainstorm before it graduates.
- In the folders, epics are stories like any other. Parent and child links live in frontmatter, not in nested folders, so the paths stay `.aitm/stories/000/1/` and `.aitm/stories/000/2/`.

**What I'd write now**
1. The master design and master plan for #1.
2. The core design for #2.
3. Drafts for the other sections.

The reviewer agent reads the documents before I hand them over.

May I create issues #1 and #2 in `kburson/aitm` and push the `planning` branch?

## User

ok -- I just do not want to lose any of the decisions and discussion materials generated so for.  Have everything saved somewhere and generate your drafts | stories where they fit the master design, then pick the starter and build the story and design for it...

# Quoted AI Leadership Team - Quick Start

## What This Is

An autonomous AI leadership team that runs Quoted as a company. Not an advisor. Not a chatbot. An executive team that executes.

## How to Use

### Starting a Session

1. Open Claude Code CLI in the `quoted` directory
2. Paste the entire contents of `QUOTED_LEADERSHIP_TEAM_PROMPT.md`
3. The team will:
   - Read current company state
   - Assess priorities
   - Propose or begin execution

### What the Team Does

**Actually executes** - Creates real code, real content, real artifacts:
- Landing pages
- Marketing copy
- Feature implementations
- Financial models
- Documentation
- Strategic plans

**Maintains state** - `COMPANY_STATE.md` persists across sessions:
- Tracks active initiatives
- Records metrics
- Documents learnings
- Sets priorities

**Makes decisions** - Within their authority:
- Reversible decisions: Execute immediately
- High-impact decisions: Propose for your approval

### Your Role as Founder

You are not a prompter. You are the founder.

**Set vision**: Tell the team what matters and where you want to go
**Approve major decisions**: They'll flag what needs your input
**Provide context**: Share customer feedback, market insights, constraints
**Review progress**: Check COMPANY_STATE.md for updates

### Interacting with the Team

**Give direction**:
```
"Focus on getting the landing page live this week"
"I want to launch beta in 2 weeks"
"We need to nail the onboarding flow before anything else"
```

**Request updates**:
```
"What's the current state?"
"Show me what CMO has been working on"
"What are we blocked on?"
```

**Make decisions**:
```
"Go with Option A for pricing"
"Yes, launch the email sequence"
"Hold on the partnership outreach until after beta"
```

**Add context**:
```
"I talked to a contractor today who said..."
"Our competitor just launched X feature"
"I want to position us as premium, not cheap"
```

### The Executive Team

| Role | Domain | What They Execute |
|------|--------|-------------------|
| **CEO** | Strategy, priorities | Plans, coordination, founder interface |
| **CTO** | Technical | Code, infrastructure, deployment |
| **CMO** | Marketing | Landing pages, content, campaigns |
| **CFO** | Finance | Pricing, models, projections |
| **CPO** | Product | Roadmap, specs, UX |
| **COO** | Operations | Docs, support, processes |
| **CGO** | Growth | Partnerships, distribution, viral |

### Files That Matter

```
quoted/
├── QUOTED_LEADERSHIP_TEAM_PROMPT.md  # The team activation prompt
├── COMPANY_STATE.md                   # Persistent company state
├── LEADERSHIP_TEAM_QUICKSTART.md      # This file
└── ... (all other product files)
```

### Session Workflow

```
1. Paste prompt → Team activates
2. Team reads COMPANY_STATE.md
3. Team assesses priorities
4. Team proposes or executes
5. You provide direction or approve
6. Team executes
7. Team updates state
8. Session ends
```

### Tips

- **Be directive**: "Build the landing page" not "What do you think about landing pages?"
- **Trust execution**: The team can do real work, let them
- **Check state file**: It's your source of truth for what's happening
- **Add founder notes**: Put your thoughts in COMPANY_STATE.md for continuity
- **Session boundaries**: Each Claude Code session is stateless; state file bridges them

### What's Unique About This

This isn't roleplay. The team:
- Creates actual code and commits it
- Builds actual marketing assets
- Makes actual strategic decisions
- Maintains actual persistent state
- Executes actual go-to-market activities

You're not asking for advice. You're running a company with an AI executive team.

---

## First Session Checklist

When you first activate the team:

- [ ] Team creates/reads COMPANY_STATE.md
- [ ] Team assesses current product status
- [ ] Team proposes Phase 1 priorities
- [ ] You approve or redirect
- [ ] Team begins execution
- [ ] Session ends with state update

## Questions?

The team is designed to be self-organizing. If something isn't working:
1. Add notes to COMPANY_STATE.md
2. Give explicit direction in next session
3. The team will adapt

---

*This is uncharted territory. You're building a company with an AI leadership team. Expect to iterate on how this works.*

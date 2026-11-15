# Position contracts

A position contract says why a seat exists, what results it owns, what it may decide, and how anyone would know it is going well. It is an operating agreement about a role. It is not an employment contract (`honesty-and-legal.md`).

## The sections

`blueprint.py position add …` records the first eight. `render` writes the document.

| Section | Flag | What goes in it |
|---|---|---|
| Identification | `--title --function --reports-to --held-by` | The seat, its function, who it answers to, who sits in it today |
| Mission | `--mission` | One sentence: why the seat exists and the result it produces |
| Accountabilities | `--accountability` ×3 to 7 | Results the seat owns, each one checkable |
| Authority | `--may`, `--needs-approval` | What it decides alone; what goes up first |
| Procedures | `--sop` | The procedures it runs, by the names used in §9 |
| Hand-offs | `--gets-from`, `--gives-to` | What it receives and from whom; what it passes on |
| Rhythm | `--daily --weekly --monthly` | The recurring work, by how often |
| Review | `--review` | How often the seat and its numbers are looked at |
| Measures | `kpi add` | Added after the position exists (`measures.md`) |
| Improvement | written by `render` | How the holder reports a procedure that does not work |
| Read and understood | written by `render` | Two signature lines |

## Mission: weak and strong

| Weak | Strong |
|---|---|
| Help with sales. | Turn qualified enquiries into clients who are a good fit for the programme. |
| Responsible for operations. | Make sure every client gets what was sold, on the date agreed, without the owner stepping in. |
| Manage the money. | Keep the business paid on time and its books ready for the accountant each month. |

A mission under eight words, or one that starts with "help", "assist" or "support", is refused.

## Accountabilities: results, not tasks

An accountability is something that is true when the seat is doing its job. Write it so a stranger could check it.

| Task (refused or weak) | Result |
|---|---|
| Follow up with leads as needed. | Every new enquiry gets a reply within one working day. |
| Handle onboarding. | Every new client has their first session booked within a week of paying. |
| Do the invoicing. | Every invoice goes out within two working days of the work being done. |
| Various admin tasks. | (not an accountability; name the results) |

Three to seven. Fewer than three and it is part of another seat. More than seven and it is two seats.

The numbers in these examples are examples of the shape. The member's own standard goes in theirs: ask "how fast is fast enough for you?" and write what they say.

## Authority

A seat with no authority sends every decision back to the owner, which is the problem being solved. For each position ask:

- "What can they decide without asking you?" (`--may`): book a call, send the standard proposal, refund up to an amount the member names.
- "What must come to you first?" (`--needs-approval`): a discount, a change to the offer, a promise outside the standard.

The top position needs no approval line.

## Procedures and hand-offs

Name procedures as they are named in §9. The script warns when a name is not found there; that is a row for the Build Plan and a job for the **SOP Creator**. A position with no procedure can be written but not handed over.

Hand-offs are where work is dropped. For each seat: what arrives, from which seat, in what state; and what leaves, to which seat, in what state. "A signed agreement and the intake form, from Sales" is a hand-off. "Stuff from sales" is not.

## How many positions

| Business | Usual number | Note |
|---|---|---|
| Solo | 4 to 6 | The owner holds all of them; the point is to see them |
| 2 to 5 people | 5 to 8 | One per function, plus the seats others already hold |
| 6 to 15 people | 8 to 14 | Split a function only when two people do different work in it |

These are working ranges for keeping the blueprint usable, not rules.

## When someone takes a seat

`blueprint.py position hold --id POS-03 --held-by "operations assistant"` records the hand-off. Then, in order: read the contract together, walk the procedures (**Training Docs**), agree the measures and the first review date, both sign. Change the contract when the seat changes; it is a living page, not a form filed once.

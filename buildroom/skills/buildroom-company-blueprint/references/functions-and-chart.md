# Functions, hats and the chart

## List the functions first

A function is a kind of work the business must do, whoever does it. Start from these seven and cut, merge or rename with the member:

| Key | Function | The work |
|---|---|---|
| `leadership` | Leadership and direction | Deciding where the business goes and what it will not do |
| `marketing` | Marketing | Being found by the right people |
| `sales` | Sales | Turning an enquiry into a client |
| `delivery` | Delivery | Doing what was sold, to the standard promised |
| `client-care` | Client care | Onboarding, questions, renewals, referrals |
| `finance` | Finance and admin | Invoices, bills, the books, the calendar |
| `people` | People and training | Finding, teaching and keeping the people who help |

A solo coach may merge client care into delivery and drop people until there is someone to train. A firm of eight may split delivery in two. Three functions is the floor: getting clients, serving them, handling the money.

## Who covers each one today

For each function: `blueprint.py function add --key sales --name "Sales" --covered-by owner`. "Covered by" is a role or a first name, never an email.

Where the owner covers it, ask for three numbers. They are the member's own estimates and only they can give them:

| Flag | Question | Scale |
|---|---|---|
| `--hours` | About how many hours a week does this take you? | hours |
| `--only-owner` | How much does it need you in particular? | 1 only I can · 3 someone skilled could · 5 anyone trained could |
| `--documented` | How written down is it? | 1 all in my head · 3 notes and templates · 5 someone could follow it today |

Never fill these in for the member. If they cannot say, leave the number out; the function is listed and not ranked.

A useful way to get honest hours: ask them to go through last week's calendar, not an average week.

## The accountability chart

One position sits at the top. One position answers for each function. Other positions report to those. The same person may hold many: the chart shows seats, and `held by` shows who is sitting in each.

`blueprint.py render` writes `blueprint/org-chart.md` as an indented list and a diagram.

Rules the check applies:

- Every function has a position that answers for it.
- Inside a function, one position has nobody above it. If two do, one of them is accountable and the other reports to it.
- Exactly one position has nobody above it at all.

## Common mistakes

- **Drawing today's people instead of the seats.** "Sam" is not a position. "Client onboarding" is, and Sam holds it.
- **A box for every task.** If a seat would have one accountability, it is part of another seat.
- **Leaving the owner out.** The owner holds positions like anyone else. Writing them down is how the owner sees how many they hold.
- **Designing for a company five times the size.** Design for the next year. The chart can grow.

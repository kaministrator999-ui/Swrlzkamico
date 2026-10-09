"""Adversarial risk/scope floor-ceiling tests; these are public, not held-out."""
from task_effort import task_effort_plan

CASES = [
    ('How do I deploy to production safely?',3,4),
    ('Fix OIDC sign-in',4,5),
    ('Fix the OAuth login flow',4,5),
    ('Quickly drop the production table',5,5),
    ('Drop the live database',5,5),
    ('Delete everything',4,5),
    ('Make a whole app with backend and frontend',4,5),
    ('Write 30 separate regression tests',3,5),
    ('Create 200 lines of code for a multi-user app',3,5),
    ('Migrate accounts into a new production database',5,5),
    ('Explain how to make an app',2,3),
    ('Explain the OAuth flow',2,3),
    ('Review this whole repository for security issues',4,5),
    ('Refactor these 5 modules for backwards compatibility',4,5),
    ('Refactor this one function',2,3),
    ('Fix our production payment gateway bug',4,5),
    ('Can you check the latest stock price',3,3),
    ('What is a stock?',1,2),
    ('What is a database?',1,2),
    ('Set up a recurring monitoring service',3,5),
    ('Fix broken session persistence',4,5),
    ('Can you explain persistence?',2,3),
    ('Please make a tutorial on TypeScript',2,3),
    ('Merge this PR into main',3,5),
    ('Refactor the database schema while keeping all existing data',4,5),
    ('Change this button color',2,2),
    ('Read the entire 700-page attachment and compare to source',3,4),
    ('Debug a race condition between two async workers',3,5),
    ('How do I learn Kotlin?',2,3),
    ('Make this answer less wordy',1,2),
    ('Teach me Rust ownership',2,3),
    ('Fix our API auth token validation',4,5),
    ('Rewrite the message to be polite',2,2),
    ('I want you to fix everything in the engine and deploy it',5,5),
    ('Design an entire software architecture',4,5),
    ('Fix tiny SQL query',2,3),
    ('Fix production SQL query without deleting data',4,5),
]
for prompt, lower, upper in CASES:
    plan=task_effort_plan(prompt)
    assert lower <= plan['tier'] <= upper, (prompt, lower, upper, plan)
    assert plan['automaticToolPermission'] is False
print(f'TASK_EFFORT_ADVERSARIAL_V182_PASS scenarios={len(CASES)}')

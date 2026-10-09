"""Fast, offline effort-tier adversarial checks. Never measures model intelligence."""
from task_effort import task_effort_plan

CASES = [
    ('Hello', 1), ('Thanks!', 1), ('What is a variable?', 1),
    ('What is production deployment?', 1),
    ('Explain what a Python function does', 2),
    ('Explain security principles', 2),
    ('What is Rust ownership?', 2),
    ('Rewrite this paragraph to be clearer', 2),
    ('Fix the typo in this function', 2),
    ('Write a tiny Python function to add two numbers', 2),
    ('Investigate why this code crashes', 3),
    ('Find root cause and test this login bug', 3),
    ('Fix this function but preserve existing behavior', 3),
    ('Research and compare current references', 3),
    ('Refactor across multiple modules and verify integration', 4),
    ('Build the entire system architecture with all dependencies', 4),
    ('Update production authentication flow', 4),
    ('Deploy this update to our production server', 5),
    ('Migrate the production database and backfill customer data', 5),
    ('Delete user accounts from the live database', 5),
]
for prompt, expected in CASES:
    plan = task_effort_plan(prompt)
    assert plan['tier'] == expected, (prompt, expected, plan)
    assert not plan['automaticToolPermission']
    assert plan['requiresAuthorization'] == (expected == 5)
    assert len(plan['reasonCodes']) <= 12
    assert plan['schema'] == 'swrlz-task-effort-plan-v1'
    assert task_effort_plan(prompt.upper())['tier'] == expected, ('case', prompt)
    assert task_effort_plan('  ' + prompt + '  ')['tier'] == expected, ('whitespace', prompt)

assert task_effort_plan('Fix this compiler failure', {'codingTask': True, 'failureEvidence': {'x': 1}})['tier'] >= 3
assert task_effort_plan('Fix this', {'needsFailureEvidence': True})['tier'] >= 3
assert task_effort_plan('') == task_effort_plan(' \t ')
assert task_effort_plan('Explain what a deployment means')['requiresAuthorization'] is False
assert task_effort_plan('Research the production database schema')['automaticToolPermission'] is False
assert task_effort_plan('x' * 7500)['tier'] >= 3
print(f'TASK_EFFORT_V182_PASS scenarios={len(CASES)} case+whitespace+source+policy')

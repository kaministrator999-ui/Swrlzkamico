"""§E v11.550: verify the UV editor already injected by v11.356.

The v11.356 patch reads the current UV preview runtime source. Reinjecting
its editor here duplicates lexical declarations and breaks the build.
"""
def apply(html):
    required=(
        '/* SE UV direct edit:',
        'function se356EditInstall()',
        'se356EditInstall();',
        'function se356EditApply(',
    )
    for token in required:
        count=html.count(token)
        if count!=1:
            raise AssertionError(('UV editor must be injected exactly once',token,count))
    return html

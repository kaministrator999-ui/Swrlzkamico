# Complete source-file delivery protocol

**Deployment status (2026-10-27):** the implementation described here is in deployed source `f925e2012ed7ece820e3272700bc6619846c2085`. Runtime/model acceptance remains scoped by [the current checkpoint](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md); dated preparation claims below are historical.

The editor/project completion checkpoint includes an observed model-formatting
failure: the candidate-only14B model's first completed draft placed bare
`file=... project=...` attributes on the first line **inside** each source fence.
Those bytes are literal file contents. They do not declare an archive filename
and can also make the returned program invalid. The unchanged draft remains
negative evidence; its SHA256 is
`45b71f63cb096af15ea0a93a932b9a1e760cd2074890f0a8fe649b7ab666e42d`.
The trial's later interrupted attempt is not a completed model result.

Both engines receive the shared file-delivery policy. It now states that the
language, relative filename and project attributes belong on the same physical
line as the opening backticks. The next line begins actual file contents. The
policy applies to the project's actual stack, including native source and
configuration files; its HTML/CSS/JavaScript examples do not require a web stack.
Bare metadata lines inside source must be corrected by the model rather than
removed or interpreted as a filename by the application.

When source checks report a missing linked/imported module, retry feedback now
explains the exact relative-path and opening-line protocol. It retains the
actual rejection and all original requirements. It does not supply an editor
implementation, fabricate a missing module, alter candidate bytes or imply a
successful build. Existing safe-path/archive validation remains authoritative.

Regression coverage inspects the shared policy for web and Android requests and
passes a real missing-module rejection through both engines' message builders.
The retry receives the protocol explanation and complete rejected candidate;
an independently supplied corrected fixture can complete normally. These checks
establish prompt/feedback delivery, not actual model instruction following or
working editor behavior. Actual native and hosted model/browser results remain
separate checkpoint evidence.

Short unlabelled terminal instructions can accompany source without becoming
invented files or replacing the requested implementation language. The shared
source-fence classifier recognizes at most four plain known-tool invocations
only after actual nonterminal source and an immediately preceding run/setup/usage
paragraph. Explicit filenames, filename comments, primary Bash, shebangs,
functions, chained/evaluated commands, TODO markers and ambiguous prose remain
source under the ordinary checks. Raw fences and command bytes remain visible
in Chat; only the actual source files enter the ZIP. This classification never
executes commands, grants tool access, repairs generated code or proves an editor
works.

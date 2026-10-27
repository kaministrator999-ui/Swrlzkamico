# Bounded completion of explicit long prose requests

The larger output allowance alone did not make the ordinary700M model follow a
1200-word request: the earlier actual trial stopped normally at about630 words.
The candidate-only1.2B comparison also stopped early. Those observations remain
negative length-following evidence; a larger model is not automatically promoted.

`hf_space/longform_completion.py` handles explicit ordinary prose word targets
between1000 and12000 words. Both engines buffer those drafts before delivery.
When a normally stopped draft misses the target, one additional model call can
produce a complete revised document from the original instructions and unchanged
draft. The feedback asks for substantive development while preserving the topic,
constraints and supported facts. The application neither pads nor concatenates
text, moves a conclusion, rewrites model output, or invents missing content.

The worker allows at most two model drafts. It deducts observed output tokens
from the original4096/8192/16384-token allowance and also checks the full next
input against the configured context and safety reserve. Provider completion
usage is preferred when supplied. Otherwise accounting is explicitly labelled a
visible-text tokenizer estimate with one stop-token margin; it is not presented
as exact provider usage. Mandatory messages and the complete draft are retained
or expansion stops for insufficient context/output room. Unknown termination,
truncation, oversize and inconsistent token observations cannot pass as complete.

Only a selected whole model draft is delivered. If a replacement is truncated,
the earlier normally stopped draft remains preferable; it still fails when it
misses the requested length. Every actual attempt, selected-attempt marker,
termination fact, measured word count, token accounting method and bounded
completion observation are recorded without putting draft text in telemetry.
A final missed target ends with `FAILED/LONGFORM_LENGTH_NOT_MET`, never a
successful whole-document completion. The visible draft remains partial for the
request. A length pass means only the measured word target and normal model stop,
not factual accuracy, originality, usefulness or document quality.

The parser excludes upper limits, exact formats, direct identity modes, code and
internal structured tasks, lyrics/poems, translation/echo/quoted source and known
non-whitespace-language targets. Very large documents remain staged work rather
than an unlimited single response. A short requested conclusion does not cancel
an otherwise explicit long-document target. The engines' existing coding,
identity, lyric, verified-file and internal GitHub workers retain their branches.

Controlled regression evidence covers full instruction/draft preservation,
whole-draft replacement, normal-stop and limit facts, honest underlength failure,
selected-draft validation, context/output bounds and ordinary/internal-task
separation through both actual engine loops. These fixtures are not actual model
quality evidence. A fresh pinned700M1200-word trial is recorded separately as
`native-700m-large-r2`; read its actual receipt before claiming improvement.

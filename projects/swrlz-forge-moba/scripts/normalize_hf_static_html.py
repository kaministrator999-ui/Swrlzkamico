"""Remove Hugging Face's observed static-host HTML metadata without altering project bytes."""
import re

_PROVIDER_SCRIPT = re.compile(
    rb'(?<=<head>)<script>window\.huggingface=\{variables:\{.*?\}\};</script>'
)
_PROVIDER_SOCIAL = re.compile(
    rb'<meta property="og:title" content="[^"<>]*">'
    rb'<meta property="og:description" content="[^"<>]*">'
    rb'<meta property="og:image" content="https://cdn-thumbnails\.huggingface\.co/social-thumbnails/spaces/kamiloki/swrlz-forge-moba\.png">'
    rb'<meta name="twitter:card" content="summary_large_image">'
    rb'<meta name="twitter:image" content="https://cdn-thumbnails\.huggingface\.co/social-thumbnails/spaces/kamiloki/swrlz-forge-moba\.png">'
)

def normalize_served_html(data: bytes) -> bytes:
    if not isinstance(data, bytes):
        raise TypeError("Expected raw HTML bytes")
    data = _PROVIDER_SCRIPT.sub(b"", data, count=1)
    return _PROVIDER_SOCIAL.sub(b"", data, count=1)

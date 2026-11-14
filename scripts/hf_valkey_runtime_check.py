"""Safe Space runtime liveness report; does not print body, secrets or logs."""
import json, os
from urllib.request import Request, urlopen
from huggingface_hub import HfApi

SPACE="kamiloki/Swyrlz"
def main():
    api=HfApi(token=os.environ["HF_TOKEN"])
    runtime=api.get_space_runtime(SPACE)
    revision=api.repo_info(SPACE,repo_type="space").sha
    status=None
    try:
        with urlopen(Request("https://kamiloki-swyrlz.hf.space/api/account/status",
                             headers={"User-Agent":"SWRLZ-ReadOnly-Health/1"}),timeout=12) as response:
            status=response.status
    except Exception as exc:
        status=type(exc).__name__
    print("SWRLZ_SPACE_RUNTIME_HEALTH "+json.dumps({"revision":revision,
          "stage":runtime.stage,"accountStatusHTTP":status,
          "operation":"READ_ONLY_NO_DATABASE_CHANGE"},default=str))
if __name__=="__main__":main()

"""Exact reviewed §X browser lane; all other candidates use the existing worker."""
import re
from hashlib import sha256

BACKEND="swrlz-x-reviewed"
X_SOURCE_SHA="__X_SOURCE_SHA__"
REVIEWED={"repaired":"__REPAIRED_SHA__","repairedById":"__ALTERNATE_SHA__"}
def candidate_hashes(project,files):
    try:from html_project_agent_v1 import verify_source
    except ImportError:from api.html_project_agent_v1 import verify_source
    return verify_source(project,files)

class ReviewedXBackend:
    name=BACKEND
    def __init__(self,fallback,*,cancel=None,diagnose=None):
        self.fallback,self.cancel,self.diagnose=fallback,cancel,diagnose
    def validate_candidate(self,project,files,canvas,proposal):
        if callable(self.cancel) and self.cancel():raise ValueError("CANCELLED")
        hashes=candidate_hashes(project,files)
        # Full tree match, never an entry-only match with extra executable files.
        selected=next((case for case,h in REVIEWED.items() if hashes=={"index.html":h}),None)
        if selected is None:
            return self.fallback().validate_candidate(project,files,canvas,proposal)
        try:
            if self.diagnose is None:
                from x_diagnostic_client import diagnose
            else:diagnose=self.diagnose
            signed=diagnose()
            d=signed["diagnostics"];suite=d["trusted_development"];case=suite[selected]
            if not (d.get("source_sha256")==X_SOURCE_SHA and suite.get("schema")=="swrlz-trusted-development-v1"
                and suite.get("arbitraryExecution") is False and suite.get("isolationVerified") is False
                and suite.get("passed") is True and case.get("passed") is True
                and case.get("fixtureSha256")==hashes["index.html"] and case.get("before")=="Ready"
                and case.get("after")=="Click passed" and case.get("pageErrors")==[]
                and re.fullmatch(r"[a-f0-9]{64}",case.get("screenshotSha256") or "")
                and re.fullmatch(r"[a-f0-9]{32}",signed.get("nonce") or "")):
                raise ValueError("X_REVIEWED_RECEIPT_MISMATCH")
        except Exception as exc:
            # Infrastructure failure is not a model defect. Preserve normal isolated validation.
            if callable(self.cancel) and self.cancel():raise ValueError("CANCELLED")
            return self.fallback().validate_candidate(project,files,canvas,proposal)
        if callable(self.cancel) and self.cancel():raise ValueError("CANCELLED")
        return {"backend":BACKEND,"receipt":{"schema":"swrlz-x-reviewed-candidate-v07",
            "project":project,"hashes":hashes,"entrySha256":hashes["index.html"],
            "browserVerified":True,"issues":[],"scope":"reviewed-single-file-fixture",
            "reviewedVariant":selected,"workerNonce":signed["nonce"],"workerSourceSha256":X_SOURCE_SHA,
            "screenshotSha256":case["screenshotSha256"],"arbitraryExecution":False,
            "isolationVerified":False,"requiresIndependentApprovalValidation":True}}

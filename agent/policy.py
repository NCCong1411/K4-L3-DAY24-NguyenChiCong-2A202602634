"""BƯỚC 3b — PEP (Policy Enforcement Point) tại tool call (15').

Cổng chặn TRƯỚC KHI tool thật sự execute. Đọc CHECKPOINTS.md (§3b).

Interface bắt buộc (tests/test_policy.py và agent/runner.py gọi trực tiếp):

    check(context: PolicyContext) -> tuple[bool, str]
        Trả về (allow, reason).
        `reason` KHÔNG BAO GIỜ được để trống — cả khi allow=True và
        allow=False. Đây là evidence audit ở Bước 4 (rubric: "Audit
        completeness = 100%" — điều kiện trượt nếu có dòng thiếu reason).

PolicyContext — 5 input gốc và các input OBO cho lớp L3:

    data_classification: str   "public" | "internal" | "restricted"
    request_purpose: str       tự do, ví dụ "reconciliation", "support-reply"
    agent_owner: str            định danh agent/run gọi tool này
    delegation_depth: int       0 = gọi trực tiếp bởi user, >0 = agent gọi agent
    egress_enabled: bool        run hiện tại có được phép gọi network không
    principal_id: str           ID người ra lệnh từ data/principals.json
    requested_tool: str         tool sắp gọi
    agent_scopes: tuple[str]    quyền tối đa của agent
    parent_scopes: tuple[str]   quyền của agent cha khi delegation_depth > 0
    expires_at: str             ISO-8601 UTC; hết hạn phải deny

Rule TỐI THIỂU bắt buộc (không được viết yếu hơn rule này):

    classification == "restricted" and egress_enabled is True  ->  DENY

Checkpoint OBO: quyền hiệu lực = principal.allowed_tools ∩ agent_scopes,
và nếu depth > 0 thì còn giao với parent_scopes. Unknown principal, scope
thiếu, run hết hạn đều deny kèm reason. Principal là fixture mô phỏng,
không phải xác thực người dùng production.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PRINCIPALS_FILE = Path(__file__).resolve().parent.parent / "data" / "principals.json"
VALID_CLASSIFICATIONS = {"public", "internal", "restricted"}


@dataclass(frozen=True)
class PolicyContext:
    data_classification: str
    request_purpose: str
    agent_owner: str
    delegation_depth: int
    egress_enabled: bool
    principal_id: str = ""
    requested_tool: str = ""
    agent_scopes: tuple[str, ...] = ()
    parent_scopes: tuple[str, ...] = ()
    expires_at: str = ""


def check(context: PolicyContext) -> tuple[bool, str]:
    """Decide whether one pending tool call is authorized.

    The policy defaults to denial.  Every return includes a short reason so a
    caller can write a complete audit entry for both allowed and denied calls.
    """
    # This minimum rule is intentionally evaluated before OBO checks: even a
    # fully authorized principal must not combine restricted data and egress.
    if context.data_classification == "restricted" and context.egress_enabled:
        return False, "restricted data cannot be sent through an egress-enabled run"

    if context.data_classification not in VALID_CLASSIFICATIONS:
        return False, f"unknown data classification: {context.data_classification!r}"
    if context.delegation_depth < 0:
        return False, "delegation depth cannot be negative"
    if not context.principal_id:
        return False, "missing principal identity"
    if not context.requested_tool:
        return False, "missing requested tool"
    if not context.request_purpose:
        return False, "missing request purpose"

    try:
        principals = json.loads(PRINCIPALS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, "principal source is unavailable or invalid"

    principal = principals.get(context.principal_id)
    if not isinstance(principal, dict):
        return False, f"unknown principal: {context.principal_id!r}"

    if context.request_purpose not in set(principal.get("purposes", ())):
        return False, "request purpose is not authorized for this principal"
    if context.requested_tool not in set(principal.get("allowed_tools", ())):
        return False, "requested tool is not authorized for this principal"
    if context.requested_tool not in set(context.agent_scopes):
        return False, "requested tool is outside the agent scope"

    if context.delegation_depth > 0:
        if context.requested_tool not in set(context.parent_scopes):
            return False, "requested tool is outside the parent scope"

    try:
        expires_at = datetime.fromisoformat(context.expires_at.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return False, "missing or invalid run expiry"
    if expires_at.tzinfo is None:
        return False, "run expiry must include a UTC offset"
    if expires_at.astimezone(timezone.utc) <= datetime.now(timezone.utc):
        return False, "run has expired"

    return True, "principal, purpose and effective scopes authorize this tool call"

"""
Accessibility Compliance Tests (WCAG 2.1)
==========================================
Runs axe-core against the target page via Playwright and asserts
zero critical/serious violations.

Key design decisions:
  • Uses the AxeResults API (.response, .generate_report()) –
    axe-playwright-python ≥0.1.5 returns an AxeResults object, NOT a dict.
  • Only FAILS CI for critical & serious impact violations.
  • Minor & moderate violations are logged as warnings (won't block pipeline).
  • Full violation report + raw JSON attached to Allure for audit trail.
  • Page load uses networkidle wait to ensure DOM is fully rendered before scan.
"""

import json
import pytest
import allure
from axe_playwright_python.sync_playwright import Axe
from utils.logger import log

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TARGET_URL = "https://example.com"
# Impact levels that should FAIL the pipeline
BLOCKING_IMPACTS = {"critical", "serious"}
# Page load timeout (ms) – generous for CI runners
PAGE_LOAD_TIMEOUT_MS = 30_000


def _categorize_violations(violations: list[dict]) -> dict[str, list[dict]]:
    """Bucket violations by axe-core impact level."""
    buckets: dict[str, list[dict]] = {
        "critical": [],
        "serious": [],
        "moderate": [],
        "minor": [],
    }
    for v in violations:
        impact = v.get("impact", "minor")
        buckets.setdefault(impact, []).append(v)
    return buckets


def _format_violation_summary(violation: dict) -> str:
    """Return a concise, human-readable summary line for a single violation."""
    nodes_count = len(violation.get("nodes", []))
    return (
        f"[{violation['impact'].upper()}] {violation['id']}: "
        f"{violation['description']}  "
        f"(help: {violation.get('helpUrl', 'N/A')})  "
        f"({nodes_count} element{'s' if nodes_count != 1 else ''} affected)"
    )


def _build_detailed_report(violations: list[dict]) -> str:
    """Build a multi-line text report suitable for Allure attachment."""
    if not violations:
        return "✅ No accessibility violations found."

    lines = [
        "=" * 72,
        "  AXE-CORE ACCESSIBILITY VIOLATION REPORT",
        "=" * 72,
        "",
    ]
    for idx, v in enumerate(violations, start=1):
        lines.append(f"  #{idx}  {v['id']}")
        lines.append(f"       Impact      : {v['impact']}")
        lines.append(f"       Description : {v['description']}")
        lines.append(f"       Help        : {v.get('helpUrl', 'N/A')}")
        lines.append(f"       WCAG Tags   : {', '.join(v.get('tags', []))}")
        for node_idx, node in enumerate(v.get("nodes", []), start=1):
            targets = ", ".join(node.get("target", []))
            snippet = node.get("html", "").replace("\n", " ").strip()
            lines.append(f"       Element {node_idx}: {targets}")
            lines.append(f"         HTML     : {snippet[:200]}")
            for msg in node.get("any", []) + node.get("all", []) + node.get("none", []):
                lines.append(f"         → {msg.get('message', '')}")
        lines.append("-" * 72)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
@allure.feature("Accessibility Testing")
@allure.story("WCAG 2.1 Compliance Audit")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("a11y", "wcag", "axe-core")
@pytest.mark.a11y
def test_accessibility_compliance(page):
    """
    Audit the target page for WCAG 2.1 accessibility violations.

    Strategy:
      1. Navigate to the page and wait for network idle.
      2. Inject axe-core and run a full-page scan.
      3. Attach the full report + raw JSON to Allure.
      4. FAIL only if critical/serious violations exist.
      5. Log moderate/minor violations as non-blocking warnings.
    """

    # ── Step 1: Navigate ──────────────────────────────────────────────────
    with allure.step(f"Navigate to {TARGET_URL}"):
        log.info(f"[A11Y] Navigating to {TARGET_URL}")
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
            page.wait_for_load_state("domcontentloaded")
            log.info("[A11Y] Page loaded successfully.")
        except Exception as exc:
            log.error(f"[A11Y] Page failed to load: {exc}")
            allure.attach(str(exc), name="Page Load Error", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Page load failed for {TARGET_URL}: {exc}")

    # ── Step 2: Run axe-core scan ─────────────────────────────────────────
    with allure.step("Inject axe-core and execute accessibility scan"):
        log.info("[A11Y] Injecting axe-core engine...")
        try:
            axe = Axe()
            results = axe.run(page)
        except Exception as exc:
            log.error(f"[A11Y] axe-core scan failed: {exc}")
            allure.attach(str(exc), name="Axe Scan Error", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"axe-core scan failed: {exc}")

    # ── Step 3: Extract violations from AxeResults ────────────────────────
    # axe-playwright-python ≥0.1.5 returns AxeResults, not a dict.
    # Access the underlying dict via .response attribute.
    with allure.step("Parse scan results"):
        response_dict = results.response
        violations = response_dict.get("violations", [])
        total_count = len(violations)
        log.info(f"[A11Y] Scan complete — {total_count} total violation(s) found.")

    # ── Step 4: Categorize by impact severity ─────────────────────────────
    with allure.step("Categorize violations by impact level"):
        buckets = _categorize_violations(violations)
        for level in ("critical", "serious", "moderate", "minor"):
            count = len(buckets[level])
            if count:
                log.info(f"[A11Y]   {level.upper()}: {count} violation(s)")

        blocking = buckets["critical"] + buckets["serious"]
        non_blocking = buckets["moderate"] + buckets["minor"]

    # ── Step 5: Log & attach reports to Allure ────────────────────────────
    with allure.step("Generate and attach violation reports"):
        # Full human-readable report (built-in method)
        try:
            axe_report = results.generate_report()
            allure.attach(
                axe_report,
                name="Axe Full Report",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            log.warning("[A11Y] generate_report() failed; using custom report.")

        # Custom detailed report
        detailed_report = _build_detailed_report(violations)
        allure.attach(
            detailed_report,
            name="Detailed Violation Report",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Raw JSON for debugging / downstream tooling
        allure.attach(
            json.dumps(violations, indent=2),
            name="Violations (JSON)",
            attachment_type=allure.attachment_type.JSON,
        )

        # Screenshot of the audited page
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="Page Screenshot (at scan time)",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            log.warning("[A11Y] Screenshot capture failed.")

    # ── Step 6: Log non-blocking warnings ─────────────────────────────────
    if non_blocking:
        with allure.step(f"⚠️  {len(non_blocking)} non-blocking (moderate/minor) violation(s)"):
            for v in non_blocking:
                summary = _format_violation_summary(v)
                log.warning(f"[A11Y] {summary}")

    # ── Step 7: Log and assert on blocking violations ─────────────────────
    if blocking:
        with allure.step(f"🚨 {len(blocking)} blocking (critical/serious) violation(s)"):
            for v in blocking:
                summary = _format_violation_summary(v)
                log.error(f"[A11Y] {summary}")

            blocking_report = _build_detailed_report(blocking)
            allure.attach(
                blocking_report,
                name="🚨 Blocking Violations",
                attachment_type=allure.attachment_type.TEXT,
            )

    with allure.step("Assert zero critical/serious accessibility violations"):
        assert len(blocking) == 0, (
            f"Accessibility audit FAILED — {len(blocking)} blocking violation(s):\n"
            + "\n".join(_format_violation_summary(v) for v in blocking)
        )

    log.info("[A11Y] ✅ Accessibility audit PASSED — no critical/serious violations.")

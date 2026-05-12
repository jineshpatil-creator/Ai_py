import pytest
import allure
from axe_playwright_python.sync_playwright import Axe
from utils.logger import log

@allure.feature("Accessibility Testing")
@allure.story("WCAG Compliance Audit")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.a11y
def test_accessibility_compliance(page):
    """
    Test the homepage for critical accessibility (WCAG) violations using axe-core.
    """
    target_url = "https://example.com"

    with allure.step(f"Navigate to {target_url}"):
        log.info(f"Navigating to {target_url} for Accessibility Audit")
        page.goto(target_url)

    with allure.step("Inject axe-core and run accessibility analysis"):
        axe = Axe()
        results = axe.run(page)

    with allure.step("Evaluate violations"):
        violations = results.violations
        log.info(f"Found {len(violations)} accessibility violations.")

        critical_violations = [v for v in violations if v["impact"] in ["critical", "serious"]]

        if critical_violations:
            log.error("CRITICAL Accessibility Violations Found:")
            violation_text = ""
            for violation in critical_violations:
                msg = f"- {violation['id']}: {violation['description']} (Impact: {violation['impact']})"
                log.error(msg)
                violation_text += msg + "\n"
            allure.attach(violation_text, name="Critical Violations", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Assert zero critical/serious violations"):
        assert len(critical_violations) == 0, f"Page failed accessibility audit with {len(critical_violations)} critical/serious violations."

Feature: Homepage Visual AI Validation
  As a QA Engineer
  I want to use AI to validate the visual layout of multiple websites
  So that I can catch UI regressions automatically

  Scenario Outline: Visual AI Validation across multiple websites
    Given I load the test data
    When I navigate to the <url>
    And I take a full-page screenshot
    Then the AI validator should confirm the page looks correct and has heading <expected_heading>

    Examples:
    | url                    | expected_heading |
    | https://example.com    | Example Domain   |
    | https://playwright.dev | Playwright       |

"""
Premium HTML Report Generator - A pytest plugin that creates a stunning
self-contained dark-mode HTML dashboard report with charts and animations.
"""
import pytest
import os
import sys
import time
import platform
from datetime import datetime, timedelta


class PremiumReportPlugin:
    """Collects test results and generates a premium HTML report."""

    def __init__(self, report_path="reports/premium_report.html"):
        self.report_path = report_path
        self.results = []
        self.session_start = None
        self.session_end = None

    def pytest_sessionstart(self, session):
        self.session_start = time.time()

    def pytest_runtest_makereport(self, item, call):
        if call.when == "call":
            markers = [m.name for m in item.iter_markers()]
            self.results.append({
                "name": item.name,
                "nodeid": item.nodeid,
                "outcome": None,  # filled by logreport
                "duration": call.duration,
                "markers": markers,
                "longrepr": str(call.excinfo.getrepr()) if call.excinfo else "",
                "start": call.start,
            })

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call" or (report.when == "setup" and report.skipped):
            markers = [m.name for m in item.iter_markers()]
            self.results.append({
                "name": item.name,
                "nodeid": item.nodeid,
                "outcome": report.outcome if report.when == "call" else "skipped",
                "duration": report.duration,
                "markers": markers,
                "longrepr": str(report.longrepr) if report.longrepr else "",
                "start": time.time(),
            })

    def pytest_sessionfinish(self, session, exitstatus):
        self.session_end = time.time()
        total_duration = self.session_end - self.session_start

        passed = sum(1 for r in self.results if r["outcome"] == "passed")
        failed = sum(1 for r in self.results if r["outcome"] == "failed")
        skipped = sum(1 for r in self.results if r["outcome"] == "skipped")
        errors = sum(1 for r in self.results if r["outcome"] not in ("passed", "failed", "skipped"))
        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        env_info = {
            "Python": platform.python_version(),
            "Platform": platform.platform(),
            "OS": platform.system(),
            "Machine": platform.machine(),
            "Pytest": pytest.__version__,
            "Node": platform.node(),
        }

        html = self._generate_html(
            passed, failed, skipped, errors, total,
            pass_rate, total_duration, env_info
        )

        os.makedirs(os.path.dirname(self.report_path) or ".", exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(html)

    def _generate_html(self, passed, failed, skipped, errors, total,
                       pass_rate, total_duration, env_info):
        now = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
        dur_str = f"{total_duration:.2f}s"

        test_rows = ""
        for i, r in enumerate(self.results):
            status_class = r["outcome"]
            icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(r["outcome"], "⚠️")
            dur = f"{r['duration']:.3f}s"
            markers_html = "".join(f'<span class="marker">{m}</span>' for m in r["markers"])
            log_html = ""
            if r["longrepr"]:
                safe_repr = r["longrepr"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                log_html = f'<div class="test-log"><pre>{safe_repr}</pre></div>'

            bar_width = min(r["duration"] / (total_duration or 1) * 100, 100)

            test_rows += f'''
            <div class="test-row {status_class}" onclick="toggleLog('log-{i}')">
                <div class="test-info">
                    <span class="test-icon">{icon}</span>
                    <div class="test-details">
                        <span class="test-name">{r["name"]}</span>
                        <span class="test-nodeid">{r["nodeid"]}</span>
                        {markers_html}
                    </div>
                </div>
                <div class="test-meta">
                    <div class="duration-bar-container">
                        <div class="duration-bar {status_class}" style="width:{bar_width}%"></div>
                    </div>
                    <span class="test-duration">{dur}</span>
                    <span class="status-badge {status_class}">{r["outcome"].upper()}</span>
                </div>
            </div>
            <div class="test-log-container" id="log-{i}">{log_html}</div>
            '''

        env_rows = ""
        for k, v in env_info.items():
            env_rows += f'<tr><td>{k}</td><td>{v}</td></tr>'

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QA Test Report — Enterprise AI Framework</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg-primary:#0a0e17;--bg-secondary:#111827;--bg-card:#1a1f2e;
  --bg-glass:rgba(26,31,46,0.7);--border:rgba(255,255,255,0.06);
  --text-primary:#f1f5f9;--text-secondary:#94a3b8;--text-muted:#64748b;
  --accent-green:#10b981;--accent-red:#ef4444;--accent-yellow:#f59e0b;
  --accent-blue:#3b82f6;--accent-purple:#8b5cf6;
  --gradient:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  --gradient-green:linear-gradient(135deg,#10b981,#059669);
  --gradient-red:linear-gradient(135deg,#ef4444,#dc2626);
  --gradient-yellow:linear-gradient(135deg,#f59e0b,#d97706);
  --gradient-blue:linear-gradient(135deg,#3b82f6,#2563eb);
  --shadow:0 8px 32px rgba(0,0,0,0.3);
  --radius:16px;--radius-sm:10px;
}}
body{{
  font-family:'Inter',sans-serif;background:var(--bg-primary);
  color:var(--text-primary);min-height:100vh;overflow-x:hidden;
}}
body::before{{
  content:'';position:fixed;top:0;left:0;width:100%;height:100%;
  background:radial-gradient(ellipse at 20% 50%,rgba(102,126,234,0.08) 0%,transparent 50%),
              radial-gradient(ellipse at 80% 20%,rgba(118,75,162,0.06) 0%,transparent 50%),
              radial-gradient(ellipse at 50% 80%,rgba(16,185,129,0.04) 0%,transparent 50%);
  pointer-events:none;z-index:0;
}}
.container{{max-width:1280px;margin:0 auto;padding:32px 24px;position:relative;z-index:1}}

/* Header */
.header{{
  text-align:center;padding:48px 24px 36px;margin-bottom:32px;
  background:var(--bg-glass);backdrop-filter:blur(20px);
  border:1px solid var(--border);border-radius:var(--radius);
  position:relative;overflow:hidden;
}}
.header::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--gradient);
}}
.header-badge{{
  display:inline-flex;align-items:center;gap:8px;padding:6px 16px;
  background:rgba(102,126,234,0.12);border:1px solid rgba(102,126,234,0.2);
  border-radius:20px;font-size:12px;font-weight:600;color:#818cf8;
  letter-spacing:1px;text-transform:uppercase;margin-bottom:16px;
}}
.header h1{{font-size:28px;font-weight:800;letter-spacing:-0.5px;margin-bottom:8px;
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.header .subtitle{{color:var(--text-secondary);font-size:14px}}
.header .timestamp{{color:var(--text-muted);font-size:12px;margin-top:8px}}

/* Stats Grid */
.stats-grid{{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:16px;margin-bottom:32px;
}}
.stat-card{{
  background:var(--bg-glass);backdrop-filter:blur(16px);
  border:1px solid var(--border);border-radius:var(--radius);
  padding:24px;position:relative;overflow:hidden;
  transition:transform 0.3s,box-shadow 0.3s;
}}
.stat-card:hover{{transform:translateY(-4px);box-shadow:var(--shadow)}}
.stat-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
}}
.stat-card.total::before{{background:var(--gradient)}}
.stat-card.passed::before{{background:var(--gradient-green)}}
.stat-card.failed::before{{background:var(--gradient-red)}}
.stat-card.skipped::before{{background:var(--gradient-yellow)}}
.stat-card.rate::before{{background:var(--gradient-blue)}}
.stat-card.duration::before{{background:var(--gradient)}}
.stat-label{{font-size:12px;font-weight:600;text-transform:uppercase;
  letter-spacing:1px;color:var(--text-muted);margin-bottom:8px}}
.stat-value{{font-size:36px;font-weight:800;letter-spacing:-1px}}
.stat-card.total .stat-value{{color:var(--accent-blue)}}
.stat-card.passed .stat-value{{color:var(--accent-green)}}
.stat-card.failed .stat-value{{color:var(--accent-red)}}
.stat-card.skipped .stat-value{{color:var(--accent-yellow)}}
.stat-card.rate .stat-value{{color:var(--accent-blue)}}
.stat-card.duration .stat-value{{color:var(--accent-purple);font-size:28px}}

/* Chart + Env Section */
.middle-section{{
  display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:32px;
}}
.panel{{
  background:var(--bg-glass);backdrop-filter:blur(16px);
  border:1px solid var(--border);border-radius:var(--radius);
  padding:28px;position:relative;overflow:hidden;
}}
.panel::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--gradient);
}}
.panel-title{{font-size:16px;font-weight:700;margin-bottom:20px;color:var(--text-primary)}}
.chart-container{{width:240px;height:240px;margin:0 auto}}

/* Environment Table */
.env-table{{width:100%;border-collapse:collapse}}
.env-table tr{{border-bottom:1px solid var(--border)}}
.env-table td{{padding:10px 12px;font-size:13px}}
.env-table td:first-child{{color:var(--text-muted);font-weight:600;width:35%}}
.env-table td:last-child{{color:var(--text-primary)}}

/* Test Results */
.results-panel{{
  background:var(--bg-glass);backdrop-filter:blur(16px);
  border:1px solid var(--border);border-radius:var(--radius);
  padding:28px;position:relative;overflow:hidden;
}}
.results-panel::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--gradient);
}}
.test-row{{
  display:flex;justify-content:space-between;align-items:center;
  padding:16px 20px;border-radius:var(--radius-sm);margin-bottom:8px;
  background:var(--bg-card);border:1px solid var(--border);
  cursor:pointer;transition:all 0.25s ease;
}}
.test-row:hover{{border-color:rgba(255,255,255,0.12);transform:translateX(4px)}}
.test-info{{display:flex;align-items:center;gap:14px;flex:1;min-width:0}}
.test-icon{{font-size:20px;flex-shrink:0}}
.test-details{{display:flex;flex-direction:column;gap:4px;min-width:0}}
.test-name{{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.test-nodeid{{font-size:11px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.marker{{
  display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;
  font-weight:600;text-transform:uppercase;letter-spacing:0.5px;
  background:rgba(139,92,246,0.15);color:#a78bfa;margin-top:2px;margin-right:4px;
}}
.test-meta{{display:flex;align-items:center;gap:16px;flex-shrink:0}}
.duration-bar-container{{
  width:80px;height:6px;background:rgba(255,255,255,0.06);
  border-radius:3px;overflow:hidden;
}}
.duration-bar{{height:100%;border-radius:3px;transition:width 1s ease}}
.duration-bar.passed{{background:var(--accent-green)}}
.duration-bar.failed{{background:var(--accent-red)}}
.duration-bar.skipped{{background:var(--accent-yellow)}}
.test-duration{{font-size:12px;color:var(--text-muted);font-weight:500;min-width:60px;text-align:right}}
.status-badge{{
  padding:4px 12px;border-radius:6px;font-size:11px;font-weight:700;
  letter-spacing:0.5px;min-width:72px;text-align:center;
}}
.status-badge.passed{{background:rgba(16,185,129,0.15);color:#34d399}}
.status-badge.failed{{background:rgba(239,68,68,0.15);color:#f87171}}
.status-badge.skipped{{background:rgba(245,158,11,0.15);color:#fbbf24}}

.test-log-container{{
  max-height:0;overflow:hidden;transition:max-height 0.35s ease;
}}
.test-log-container.open{{max-height:600px;overflow-y:auto}}
.test-log{{
  margin:0 0 8px;padding:16px 20px;border-radius:0 0 var(--radius-sm) var(--radius-sm);
  background:#0d1117;border:1px solid var(--border);border-top:none;
}}
.test-log pre{{
  font-family:'JetBrains Mono','Fira Code',monospace;font-size:12px;
  color:#f87171;white-space:pre-wrap;word-break:break-word;line-height:1.6;
}}

/* Footer */
.footer{{
  text-align:center;padding:24px;margin-top:32px;
  color:var(--text-muted);font-size:12px;
}}
.footer a{{color:#818cf8;text-decoration:none}}

/* Animations */
@keyframes fadeInUp{{
  from{{opacity:0;transform:translateY(20px)}}
  to{{opacity:1;transform:translateY(0)}}
}}
.stat-card,.panel,.test-row{{animation:fadeInUp 0.5s ease both}}
.stat-card:nth-child(2){{animation-delay:0.05s}}
.stat-card:nth-child(3){{animation-delay:0.1s}}
.stat-card:nth-child(4){{animation-delay:0.15s}}
.stat-card:nth-child(5){{animation-delay:0.2s}}
.stat-card:nth-child(6){{animation-delay:0.25s}}

@media(max-width:768px){{
  .middle-section{{grid-template-columns:1fr}}
  .stats-grid{{grid-template-columns:repeat(2,1fr)}}
}}
</style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <div class="header">
    <div class="header-badge">🤖 AI-Powered QA</div>
    <h1>Enterprise AI Visual Testing Framework</h1>
    <div class="subtitle">Automated Test Execution Report</div>
    <div class="timestamp">Generated on {now}</div>
  </div>

  <!-- Stats Grid -->
  <div class="stats-grid">
    <div class="stat-card total"><div class="stat-label">Total Tests</div><div class="stat-value">{total}</div></div>
    <div class="stat-card passed"><div class="stat-label">Passed</div><div class="stat-value">{passed}</div></div>
    <div class="stat-card failed"><div class="stat-label">Failed</div><div class="stat-value">{failed}</div></div>
    <div class="stat-card skipped"><div class="stat-label">Skipped</div><div class="stat-value">{skipped}</div></div>
    <div class="stat-card rate"><div class="stat-label">Pass Rate</div><div class="stat-value">{pass_rate:.1f}%</div></div>
    <div class="stat-card duration"><div class="stat-label">Duration</div><div class="stat-value">{dur_str}</div></div>
  </div>

  <!-- Chart + Environment -->
  <div class="middle-section">
    <div class="panel">
      <div class="panel-title">📊 Results Distribution</div>
      <div class="chart-container"><canvas id="resultsChart"></canvas></div>
    </div>
    <div class="panel">
      <div class="panel-title">🖥️ Environment</div>
      <table class="env-table">{env_rows}</table>
    </div>
  </div>

  <!-- Test Results -->
  <div class="results-panel">
    <div class="panel-title">🧪 Test Results ({total} tests)</div>
    {test_rows}
  </div>

  <div class="footer">
    Powered by <a href="#">Enterprise AI Visual Testing Framework</a> &bull; Playwright + Gemini AI
  </div>
</div>

<script>
function toggleLog(id){{
  document.getElementById(id).classList.toggle('open');
}}
const ctx=document.getElementById('resultsChart');
if(ctx){{
  new Chart(ctx,{{
    type:'doughnut',
    data:{{
      labels:['Passed','Failed','Skipped'],
      datasets:[{{
        data:[{passed},{failed},{skipped}],
        backgroundColor:['#10b981','#ef4444','#f59e0b'],
        borderColor:['#059669','#dc2626','#d97706'],
        borderWidth:2,hoverOffset:8
      }}]
    }},
    options:{{
      responsive:true,maintainAspectRatio:true,
      cutout:'65%',
      plugins:{{
        legend:{{position:'bottom',labels:{{color:'#94a3b8',padding:16,font:{{family:'Inter',size:12}}}}}},
      }}
    }}
  }});
}}
</script>
</body>
</html>'''


def pytest_configure(config):
    """Register the premium report plugin."""
    report_path = config.getoption("--premium-report", default=None)
    if report_path is None:
        report_path = config.getini("premium_report_path") or "reports/premium_report.html"
    config._premium_report = PremiumReportPlugin(report_path)
    config.pluginmanager.register(config._premium_report)


def pytest_addoption(parser):
    """Add command line option for premium report path."""
    group = parser.getgroup("premium-report", "Premium HTML Report")
    group.addoption(
        "--premium-report",
        action="store",
        default=None,
        help="Path to generate the premium HTML report (default: reports/premium_report.html)",
    )
    parser.addini(
        "premium_report_path",
        help="Path to generate the premium HTML report",
        default="reports/premium_report.html",
    )

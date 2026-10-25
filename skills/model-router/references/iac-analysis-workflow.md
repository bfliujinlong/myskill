IaC analysis workflow (Lilly customer, 2026-09-28 verified)
Trigger: user provides /data/cloud-docs/uploads/lilly交付物20260625.zip
Steps: unzip -o <zip> -d /tmp/; find . -name '*.tf' -o '*.py' -o '*.yaml'; claude -p "analyze <path>"; if empty (approval/unicode block) use real file contents to write ~/lilly-iac-analysis.md
Pitfalls: claude binary at ~/.npm-global/bin (PATH missing); codex ARM64 always missing; inner zip needs second unzip; Claude call may return empty — have manual analysis backup

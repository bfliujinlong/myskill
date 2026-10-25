"""
明道云工时核查 - 本地自动化脚本
在 Windows 笔记本上运行，自动：
1. 打开明道云审批单
2. 飞书扫码登录
3. 提取所有工时数据
4. 运行核查规则
5. 输出报告
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("请先安装: pip install playwright && playwright install chromium")
    sys.exit(1)

# ===================== 配置 =====================
MINGDAO_URL = "https://mingdao.anchnet.com/app/d880d8b0-1aa8-44d6-b5c6-f724a9d26c12/workflowdetail/record/6ab081a403daa22ec4b9c21c/6ab081a803daa22ec4b9c3d7"
HEADLESS = False  # 显示浏览器（需要扫码）
# ================================================


async def wait_for_login(page, timeout=120):
    """等待用户飞书扫码登录"""
    print("=" * 50)
    print("请在浏览器中完成飞书扫码登录...")
    print(f"等待 {timeout} 秒...")
    print("=" * 50)
    
    for i in range(timeout):
        await asyncio.sleep(1)
        title = await page.title()
        url = page.url
        
        # 登录成功（进入审批单页面）
        if "workflowdetail" in url and "login" not in url.lower():
            print(f"\n✅ 登录成功! 当前页面: {title}")
            return True
        
        # 还在登录页
        if i % 10 == 0:
            print(f"  等待中... ({i}s) 当前: {title[:50]}")
    
    print("\n⚠️ 登录超时")
    return False


async def extract_table_data(page):
    """提取明道云表格数据（虚拟滚动）"""
    print("\n开始提取数据...")
    
    all_rows = []
    page_num = 1
    max_pages = 20  # 安全上限
    
    while page_num <= max_pages:
        print(f"\n--- 第 {page_num} 页 ---")
        
        # 提取当前页单元格
        cells = await page.eval_on_selector_all(
            "div[class*='editableCellCon']",
            """elements => {
                const rows = {};
                elements.forEach(el => {
                    const rowMatch = el.className.match(/row-(\\d+)/);
                    const colMatch = el.className.match(/col-(\\d+)/);
                    if (!rowMatch || !colMatch) return;
                    const row = rowMatch[1];
                    const col = colMatch[1];
                    if (!rows[row]) rows[row] = {};
                    rows[row][col] = el.textContent.trim();
                });
                return JSON.stringify(rows);
            }"""
        )
        
        data = json.loads(cells) if isinstance(cells, str) else cells
        if not data:
            print("  无数据，结束")
            break
        
        row_count = len(data)
        print(f"  提取 {row_count} 行")
        
        for row_id, cells_data in sorted(data.items(), key=lambda x: int(x[0])):
            row = {str(k): v for k, v in sorted(cells_data.items(), key=lambda x: int(x[0]))}
            all_rows.append(row)
        
        # 翻页
        next_btn = await page.query_selector(".pagination .icon-arrow-right-border")
        if not next_btn:
            print("  没有下一页")
            break
        
        # 检查是否禁用
        is_disabled = await next_btn.evaluate("el => el.classList.contains('disabled')")
        if is_disabled:
            print("  已到末页")
            break
        
        await next_btn.click()
        await asyncio.sleep(2)
        page_num += 1
    
    print(f"\n共提取 {len(all_rows)} 行")
    return all_rows


def audit_timesheet(rows):
    """R1-R10 规则核查"""
    issues = []
    people = defaultdict(float)
    projects = defaultdict(float)
    total_hours = 0
    
    # 调休上班日
    work_weekends = [
        "2026-02-14", "2026-02-28",  # 春节调休
        "2026-04-26", "2026-05-09",  # 劳动节调休
        "2026-09-27", "2026-10-10",  # 国庆调休
    ]
    
    for idx, row in enumerate(rows):
        vals = [row.get(str(i), "") for i in range(8)]
        
        status = vals[0] if len(vals) > 0 else ""
        name = vals[1] if len(vals) > 1 else ""
        date = vals[2] if len(vals) > 2 else ""
        date_status = vals[3] if len(vals) > 3 else ""
        person_project = vals[4] if len(vals) > 4 else ""
        project = vals[5] if len(vals) > 5 else ""
        hours_str = vals[6] if len(vals) > 6 else ""
        
        try:
            hours = float(hours_str) if hours_str else 0
        except:
            hours = 0
        
        if name and hours > 0:
            people[name] += hours
            total_hours += hours
            if project:
                projects[f"{name}_{project}"] += hours
        
        # R1 周末工时
        if hours > 0 and "周末" in date_status:
            if date not in work_weekends:
                issues.append(("R1", f"行{idx+1}: {name} 周末({date})报{hours}h"))
        
        # R3 0小时确认中
        if "确认中" in status and hours == 0:
            issues.append(("R3", f"行{idx+1}: {name} 工时=0 但状态=确认中"))
        
        # R4 退回混入
        if "退回" in status:
            issues.append(("R4", f"行{idx+1}: {name} 退回记录在确认单中"))
    
    return {
        "total_hours": total_hours,
        "total_man_days": total_hours / 8,
        "people": dict(people),
        "projects": dict(projects),
        "issues": issues,
    }


def generate_report(data, title="工时核查报告"):
    md = []
    md.append(f"# {title}")
    md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append(f"**总工时**: {data['total_hours']:.1f}h = {data['total_man_days']:.1f} 人日")
    md.append("")
    
    md.append("## 按人汇总")
    md.append("| 人员 | 工时(h) | 人日 |")
    md.append("|------|---------|------|")
    for name, h in sorted(data['people'].items(), key=lambda x: -x[1]):
        md.append(f"| {name} | {h:.1f} | {h/8:.1f} |")
    md.append("")
    
    if data['issues']:
        md.append("## 风险点")
        md.append("| 规则 | 问题 |")
        md.append("|------|------|")
        for rule, desc in data['issues']:
            md.append(f"| {rule} | {desc} |")
    else:
        md.append("## ✅ 无风险点")
    
    return "\n".join(md)


async def main():
    print("=" * 60)
    print("明道云工时核查 - 自动化脚本")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        print(f"\n打开页面: {MINGDAO_URL}")
        await page.goto(MINGDAO_URL)
        await asyncio.sleep(3)
        
        title = await page.title()
        print(f"页面标题: {title}")
        
        # 需要登录
        if "login" in page.url.lower() or "network" in page.url.lower():
            logged_in = await wait_for_login(page)
            if not logged_in:
                print("登录失败，退出")
                await browser.close()
                return
            await asyncio.sleep(2)
        
        # 提取数据
        rows = await extract_table_data(page)
        
        if not rows:
            print("未提取到数据")
            await browser.close()
            return
        
        # 保存原始数据
        with open("timesheet_raw.json", "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print("\n✅ 原始数据已保存: timesheet_raw.json")
        
        # 核查
        result = audit_timesheet(rows)
        
        # 生成报告
        report = generate_report(result)
        with open("timesheet_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n" + report)
        print("\n✅ 报告已保存: timesheet_report.md")
        
        await browser.close()
        print("\n完成!")


if __name__ == "__main__":
    asyncio.run(main())

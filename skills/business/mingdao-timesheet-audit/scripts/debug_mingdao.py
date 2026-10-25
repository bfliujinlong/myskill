"""
明道云工时核查 - 调试版
"""
import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

MINGDAO_URL = "https://mingdao.anchnet.com/app/d880d8b0-1aa8-44d6-b5c6-f724a9d26c12/workflowdetail/record/6ab081a403daa22ec4b9c21c/6ab081a803daa22ec4b9c3d7"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"打开: {MINGDAO_URL}")
        await page.goto(MINGDAO_URL)
        await asyncio.sleep(5)
        
        title = await page.title()
        url = page.url
        print(f"标题: {title}")
        print(f"URL: {url}")
        
        # 截图
        await page.screenshot(path="debug_screenshot.png")
        print("截图: debug_screenshot.png")
        
        # 保存 HTML
        html = await page.content()
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: debug_page.html ({len(html)} chars)")
        
        # 查找可能的表格元素
        selectors = [
            "div[class*='editableCellCon']",
            "div[class*='cell']",
            "div[class*='grid']",
            "table",
            ".table",
            "[class*='table']",
            "[class*='grid']",
            "[class*='cell']",
        ]
        
        for sel in selectors:
            try:
                count = await page.locator(sel).count()
                if count > 0:
                    print(f"  找到 {count} 个 '{sel}'")
                    # 取前3个的内容
                    for i in range(min(3, count)):
                        text = await page.locator(sel).nth(i).text_content()
                        print(f"    [{i}]: {text[:100]}")
            except Exception as e:
                pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

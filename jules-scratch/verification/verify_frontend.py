from playwright.sync_api import sync_playwright, expect
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + os.path.abspath('frontend/index.html'))
        expect(page.locator("h1")).to_have_text("URL Checker")
        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

run()

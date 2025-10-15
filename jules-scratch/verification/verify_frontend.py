from playwright.sync_api import sync_playwright, expect
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + os.path.abspath('frontend/index.html'))
        page.get_by_placeholder("Enter a URL").fill("https://www.google.com")
        page.get_by_role("button", name="Check").click()

        try:
            # Wait for the specific element to appear
            expect(page.locator("#credibility-analysis h2")).to_contain_text("Credibility Analysis", timeout=15000)
            page.screenshot(path="jules-scratch/verification/verification.png")
        except Exception as e:
            # If it fails, print the content of the results div for debugging
            results_content = page.locator("#results").inner_html()
            print(f"Verification failed. Content of results div: {results_content}")
            raise e
        finally:
            browser.close()

run()

from playwright.sync_api import sync_playwright
import time

def screenshot_url(url, path="screenshot.png", wait_seconds=3):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 👈 headless=False to seem real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",  # 👈 pretend to be Chrome
            viewport={'width': 1280, 'height': 800},  # 👈 normal screen size
            locale='en-US',
            timezone_id='America/New_York',
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle")

        time.sleep(wait_seconds)  # Let it fully render

        page.screenshot(path=path)
        browser.close()

urls = {
    "reddit_img_url": 'https://www.reddit.com/r/github/comments/1iz98iv/saw_a_post_yesterday_about_having_difficulty_to/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button',
    "reddit_vid_url": 'https://www.reddit.com/r/indiegames/comments/1jsrbyg/made_a_new_trailer_for_my_game_dust_front_rts/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button',
    "twitter_img_url": 'https://x.com/MarioNawfal/status/1916338182854967560',
    "twitter_vid_url": 'https://x.com/bruce_barrett/status/1916259796740657254',
    "twitter_txt_url": 'https://x.com/Tazerface16/status/1916571948198552005',
    "pinterest_img_url": 'https://pin.it/6QXMdGEqp',
    "pinterest_vid_url": 'https://pin.it/1c8g1AQ5g',
    "web_url1": 'https://screenshotone.com/',
    "web_url2": 'https://www.steele.blue/playwright-on-lambda/',
    "web_url3": 'https://www.anandtech.com/show/8523/the-new-motorola-moto-x-2014-review/2'
}
for url_name, url in urls.items():
    print(f"Taking screenshot of {url_name}...")
    screenshot_url(url, f"{url_name}.png")

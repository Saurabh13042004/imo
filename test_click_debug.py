"""Debug script to test clicking behavior on Google Shopping reviews."""

import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    """Test click behavior."""
    
    # Your actual Google Shopping URL
    url = "https://www.google.com/shopping/product/1234/reviews"  # Replace with actual
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Set to False to see what happens
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"Loading {url}")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)
            
            # Check initial review count
            count_script = """
                () => {
                    const container = document.querySelector('div[jsname="Vjrt5"][data-ved]');
                    if (!container) return {error: "container not found"};
                    const reviews = container.querySelectorAll('div[data-attrid="user_review"]');
                    return {count: reviews.length};
                }
            """
            
            result = await page.evaluate(count_script)
            logger.info(f"Initial review count: {result}")
            
            # Find the button
            button_info_script = """
                () => {
                    const btn = document.querySelector('div[role="button"][jsaction*="trigger.MS0zad"]');
                    if (!btn) return {error: "button not found"};
                    
                    const rect = btn.getBoundingClientRect();
                    const style = window.getComputedStyle(btn);
                    
                    return {
                        found: true,
                        text: btn.textContent.trim().slice(0, 50),
                        visible: rect.height > 0 && style.display !== 'none',
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        display: style.display,
                        visibility: style.visibility,
                        jsaction: btn.getAttribute('jsaction'),
                        html: btn.outerHTML.slice(0, 200)
                    };
                }
            """
            
            btn_info = await page.evaluate(button_info_script)
            logger.info(f"Button info: {btn_info}")
            
            if btn_info.get('found'):
                logger.info("\n=== ATTEMPTING CLICK ===")
                
                btn_locator = page.locator('div[role="button"][jsaction*="trigger.MS0zad"]')
                await btn_locator.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)
                
                logger.info("Trying dispatch_event('click')...")
                await btn_locator.dispatch_event('click')
                logger.info("✓ dispatch_event executed")
                
                await asyncio.sleep(2)
                
                result_after = await page.evaluate(count_script)
                logger.info(f"Review count after click: {result_after}")
                
                if result_after.get('count', 0) > result.get('count', 0):
                    logger.info("✓✓✓ SUCCESS! Count increased!")
                else:
                    logger.warning("✗✗✗ FAILURE! Count did not increase")
                    
                    # Try alternative click
                    logger.info("\nTrying mouse.click()...")
                    box = await btn_locator.bounding_box()
                    if box:
                        cx = box['x'] + box['width'] / 2
                        cy = box['y'] + box['height'] / 2
                        await page.mouse.click(cx, cy)
                        logger.info(f"✓ mouse.click({cx:.0f}, {cy:.0f}) executed")
                        
                        await asyncio.sleep(2)
                        result_after2 = await page.evaluate(count_script)
                        logger.info(f"Review count after mouse click: {result_after2}")
                        
                        if result_after2.get('count', 0) > result.get('count', 0):
                            logger.info("✓✓✓ mouse.click() WORKED!")
            
            # Keep browser open so you can see what happened
            logger.info("\n=== Browser will stay open for 30 seconds ===")
            await asyncio.sleep(30)
            
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

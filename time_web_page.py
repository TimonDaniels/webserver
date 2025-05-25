import asyncio
import aiohttp
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

async def measure_page_load(url):
    """Measure concurrent page load time like a real browser"""
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Get main HTML first
        print(f"Loading {url}...")
        html_start = time.time()
        async with session.get(url) as response:
            html_content = await response.text()
        html_time = time.time() - html_start
        print(f"HTML: {html_time:.3f}s")
        
        # Parse HTML to find resources
        soup = BeautifulSoup(html_content, 'html.parser')
        resource_urls = []
        
        # Collect all resource URLs
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            if href := link.get('href'):
                resource_urls.append((urljoin(url, href), "CSS"))
        
        for script in soup.find_all('script', {'src': True}):
            if src := script.get('src'):
                resource_urls.append((urljoin(url, src), "JS"))
        
        for img in soup.find_all('img', {'src': True}):
            if src := img.get('src'):
                resource_urls.append((urljoin(url, src), "IMG"))
        
        # Load all resources concurrently
        if resource_urls:
            print("Loading resources concurrently...")
            tasks = [load_resource(session, url, rtype) for url, rtype in resource_urls]
            resource_times = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            resource_times = []
        
        total_time = time.time() - start_time
        
        print(f"\n--- Page Load Summary ---")
        print(f"HTML time: {html_time:.3f}s")
        print(f"Resources: {len(resource_urls)} files")
        print(f"Total time: {total_time:.3f}s")
        
        valid_times = [t for t in resource_times if isinstance(t, float)]
        if valid_times:
            print(f"Fastest resource: {min(valid_times):.3f}s")
            print(f"Slowest resource: {max(valid_times):.3f}s")

async def load_resource(session, url, resource_type):
    """Load a single resource and time it"""
    try:
        start = time.time()
        async with session.get(url) as response:
            await response.read()
        duration = time.time() - start
        print(f"{resource_type}: {duration:.3f}s")
        return duration
    except Exception as e:
        print(f"{resource_type} failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(measure_page_load("http://localhost:8080"))
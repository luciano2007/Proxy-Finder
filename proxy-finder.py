import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None

def parse_table_proxies(html, ip_col=0, port_col=1, scheme_col=None, version_col=None):
    proxies = []
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        ip = cols[ip_col].text.strip()
        port = cols[port_col].text.strip()
        scheme = None
        if scheme_col is not None:
            scheme_text = cols[scheme_col].text.strip().lower()
            scheme = "https" if scheme_text == "yes" else "http"
        version = cols[version_col].text.strip().lower() if version_col else None

        if version in ("socks4", "socks5"):
            proxies.append((version, ip, int(port)))
        elif scheme in ("http", "https"):
            proxies.append((scheme, ip, int(port)))
        else:
            proxies.append(("http", ip, int(port)))
    return proxies

def fetch_proxy_list_download_api(url, scheme):
    proxies = []
    html = fetch_html(url)
    if not html:
        return proxies
    for line in html.splitlines():
        if line.strip():
            parts = line.strip().split(":")
            if len(parts) == 2:
                ip, port = parts
                proxies.append((scheme, ip, int(port)))
    return proxies

def fetch_proxies():
    all_proxies = []

    urls_and_parsers = [
        ("https://www.socks-proxy.net/", {"version_col":4}),
        ("https://free-proxy-list.net/socks-proxies.html", {"version_col":4}),
        ("https://free-proxy-list.net/", {"scheme_col":6}),
        ("https://www.us-proxy.org/", {"scheme_col":6}),
        ("https://www.sslproxies.org/", {"scheme_col":6}),
        ("https://www.cool-proxy.net/proxies/http_proxy_list/country_code:all/", {"ip_col":1, "port_col":2, "scheme_col":5}),
        ("https://spys.one/en/free-proxy-list/", {"ip_col":0, "port_col":1})  # NEW SOURCE
    ]

    # Parse HTML-based sources
    for url, params in urls_and_parsers:
        html = fetch_html(url)
        if html:
            all_proxies += parse_table_proxies(html, **params)

    # API-based proxy lists
    all_proxies += fetch_proxy_list_download_api("https://www.proxy-list.download/api/v1/get?type=socks4", "socks4")
    all_proxies += fetch_proxy_list_download_api("https://www.proxy-list.download/api/v1/get?type=socks5", "socks5")
    all_proxies += fetch_proxy_list_download_api("https://www.proxy-list.download/api/v1/get?type=http", "http")
    all_proxies += fetch_proxy_list_download_api("https://www.proxy-list.download/api/v1/get?type=https", "https")

    # Proxyscrape API
    proxyscrape_urls = [
        ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all", "http"),
        ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all", "https"),
        ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all", "socks4"),
        ("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all", "socks5")
    ]
    for url, scheme in proxyscrape_urls:
        all_proxies += fetch_proxy_list_download_api(url, scheme)

    # Geonode free proxy JSON
    try:
        resp = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("data", []):
                scheme = item.get("protocols", ["http"])[0]
                ip = item.get("ip")
                port = item.get("port")
                if ip and port:
                    all_proxies.append((scheme, ip, int(port)))
    except Exception:
        pass

    return all_proxies

def check_proxy(proxy):
    scheme, ip, port = proxy
    proxy_url = f"{scheme}://{ip}:{port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    test_urls = [
        "https://www.google.com",
        "http://example.com",
        "http://httpbin.org/ip"
    ]

    for url in test_urls:
        try:
            resp = requests.get(url, proxies=proxies, timeout=10)
            if resp.status_code == 200:
                return proxy_url
        except Exception:
            continue
    return None

def main():
    try:
        num_to_print = int(input("Enter how many working proxies you want printed: "))
        if num_to_print <= 0:
            print("Number must be positive.")
            return
    except ValueError:
        print("Invalid input.")
        return

    print("Fetching proxies from multiple trusted sources (this may take some time)...")
    proxies = fetch_proxies()
    print(f"Total proxies fetched: {len(proxies)}")
    print("Checking proxies now (this can take a while)...")

    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            if result:
                working_proxies.append(result)
            if i % 50 == 0:
                print(f"Checked {i} proxies, found {len(working_proxies)} working so far...")
            if len(working_proxies) >= num_to_print:
                break

    print(f"\nFound {len(working_proxies)} working proxies.")
    print(f"Printing first {min(num_to_print, len(working_proxies))} proxies:\n")
    for proxy in working_proxies[:num_to_print]:
        print(proxy)

if __name__ == "__main__":
    main()

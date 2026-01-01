# Proxy Finder

A simple, interactive Python script that fetches small batches of free proxies (IP:port) from public "proxy list" websites. The user just runs the script, chooses how many proxies to grab, and gets a list that can be reused in other tools or scripts.

## Overview

Proxy Finder is a **prototype** proxy scraper for quickly grabbing a handful of fresh proxies (usually 1–15) from multiple public sources.

The current version is mainly a blueprint: the original sites it scraped are now dead/changed and need to be swapped out for newer sources.

## Features

- Simple CLI flow: run the script and enter how many proxies you want (e.g. 1–15).
- Scrapes multiple public "free proxy list" style sites and returns IP:port pairs.
- Designed as a starting point for adding your own sources, filters, and validation logic.

## Status and Limitations

- **Prototype / legacy code**: original scraping targets are expired or have changed layout, so the script will likely return few or no results without updates.
- No built‑in proxy checking or speed/anonymity tests; it only collects candidates.
- Intended for educational and lab use; reliability depends entirely on the upstream free proxy sites.

## Usage

1. Clone the repo:
   ```bash
   git clone https://github.com/luciano2007/Proxy-Finder.git
   cd Proxy-Finder
   ```

2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python proxy_finder.py
   ```

4. When prompted, enter how many proxies you want (recommended: 1–15).

5. The script will scrape the configured sites and print or save the collected proxies (implementation‑dependent; update README once finalized in code).

## Updating Proxy Sources

Because the original target sites are expired, you are expected to:

- Replace the old URLs in the script with newer public proxy lists (for example, similar to the ones used in other open‑source proxy scrapers).
- Adjust the HTML parsing / selectors for each new site layout.
- Optionally bolt on:
  - A proxy checker (HTTP/HTTPS/SOCKS, timeout, concurrency).
  - Filters (country, protocol, anonymity, HTTPS‑only).
  - Output formats (plain text, JSON, CSV) for use in other tools.

## Legal and Ethical Use

This project is for educational, research, and legitimate testing purposes only.

Only use proxies and any traffic you generate in environments and on systems where you have explicit permission to do so.

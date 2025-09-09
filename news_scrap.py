#!/usr/bin/env python3
"""
NewsCrap - Google News Scraper CLI
"""
import argparse
import csv
import json
import sqlite3
import logging
import time
import random
import re
import schedule
import sys
from datetime import datetime
from urllib.parse import urlparse, quote_plus
from typing import List, Dict, Any, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import markdown
from jinja2 import Template

class GoogleNewsScraper:
    def __init__(self, verbose=False, proxy_list=None, user_agents=None):
        self.verbose = verbose
        self.proxy_list = proxy_list or []
        self.user_agents = user_agents or []
        self.ua = UserAgent()
        
        # Setup logging
        logging_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=logging_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def rotate_user_agent(self) -> str:
        """Rotate user agents for requests"""
        if self.user_agents:
            return random.choice(self.user_agents)
        return self.ua.random
    
    def get_proxy(self) -> Optional[Dict]:
        """Get a random proxy from the list"""
        if self.proxy_list:
            proxy_str = random.choice(self.proxy_list)
            return {
                'http': proxy_str,
                'https': proxy_str
            }
        return None
    
    def make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rotation"""
        headers = {
            'User-Agent': self.rotate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        for attempt in range(max_retries):
            try:
                proxy = self.get_proxy()
                self.logger.debug(f"Request attempt {attempt + 1} for {url}")
                response = requests.get(
                    url, 
                    headers=headers, 
                    proxies=proxy,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    self.logger.warning("Rate limited. Waiting before retry...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"HTTP Error {response.status_code} for {url}")
                    
            except requests.RequestException as e:
                self.logger.error(f"Request failed: {e}")
            
            # Wait before retry
            time.sleep(random.uniform(1, 3))
        
        self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    def parse_article_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats from Google News"""
        if not date_str:
            return None
            
        # Handle relative times
        if 'hour' in date_str or 'minute' in date_str or 'just now' in date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Handle specific date formats
        try:
            # Try to parse various date formats
            date_formats = [
                '%b %d, %Y', '%d %b %Y', '%Y-%m-%d', 
                '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y'
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            # If all else fails, return as-is
            return date_str
        except Exception as e:
            self.logger.warning(f"Failed to parse date '{date_str}': {e}")
            return date_str
    
    def scrape_articles(self, keyword: str, max_articles: int = 10, domain_filter: str = None) -> List[Dict]:
        """Scrape articles for a given keyword"""
        articles = []
        seen_urls = set()
        page = 0
        
        self.logger.info(f"Starting scrape for keyword: {keyword}")
        
        while len(articles) < max_articles:
            # Build Google News search URL
            start = page * 10
            search_url = f"https://www.google.com/search?q={quote_plus(keyword)}&tbm=nws&start={start}"
            
            self.logger.debug(f"Fetching page {page + 1} for '{keyword}'")
            response = self.make_request(search_url)
            
            if not response:
                self.logger.error(f"Failed to fetch results page {page + 1}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result_containers = soup.find_all('div', class_='SoaBEf')
            
            if not result_containers:
                self.logger.info("No more results found")
                break
            
            for container in result_containers:
                if len(articles) >= max_articles:
                    break
                
                try:
                    # Extract article details
                    link_element = container.find('a')
                    if not link_element:
                        continue
                    
                    url = link_element.get('href')
                    if not url or url in seen_urls:
                        continue
                    
                    # Apply domain filter if specified
                    if domain_filter:
                        parsed_url = urlparse(url)
                        if domain_filter not in parsed_url.netloc:
                            continue
                    
                    title = link_element.find('div', role='heading').get_text() if link_element.find('div', role='heading') else ''
                    
                    # Extract snippet
                    snippet_div = container.find('div', class_='n0jPhd')
                    snippet = snippet_div.get_text() if snippet_div else ''
                    
                    # Extract date
                    date_span = container.find('span', class_='OSrXXb')
                    date_published = self.parse_article_date(date_span.get_text() if date_span else '')
                    
                    article_data = {
                        'keyword': keyword,
                        'url': url,
                        'title': title,
                        'date_published': date_published,
                        'snippet': snippet,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article_data)
                    seen_urls.add(url)
                    self.logger.debug(f"Scraped article: {title[:50]}...")
                    
                except Exception as e:
                    self.logger.error(f"Error parsing article: {e}")
                    continue
            
            page += 1
            # Add delay between pages to avoid rate limiting
            time.sleep(random.uniform(1, 3))
        
        self.logger.info(f"Scraped {len(articles)} articles for '{keyword}'")
        return articles
    
    def save_to_csv(self, articles: List[Dict], filename: str):
        """Save articles to CSV file"""
        if not articles:
            self.logger.warning("No articles to save")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['keyword', 'url', 'title', 'date_published', 'snippet', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(articles)
            
            self.logger.info(f"Saved {len(articles)} articles to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
    
    def save_to_json(self, articles: List[Dict], filename: str):
        """Save articles to JSON file"""
        if not articles:
            self.logger.warning("No articles to save")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(articles, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(articles)} articles to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
    
    def save_to_sqlite(self, articles: List[Dict], db_file: str):
        """Save articles to SQLite database"""
        if not articles:
            self.logger.warning("No articles to save")
            return
        
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            
            # Create table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT,
                    url TEXT UNIQUE,
                    title TEXT,
                    date_published TEXT,
                    snippet TEXT,
                    scraped_at TEXT
                )
            ''')
            
            # Insert articles
            for article in articles:
                try:
                    c.execute('''
                        INSERT OR IGNORE INTO articles 
                        (keyword, url, title, date_published, snippet, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        article['keyword'],
                        article['url'],
                        article['title'],
                        article['date_published'],
                        article['snippet'],
                        article['scraped_at']
                    ))
                except sqlite3.Error as e:
                    self.logger.error(f"Error inserting article: {e}")
            
            conn.commit()
            conn.close()
            self.logger.info(f"Saved {len(articles)} articles to SQLite database {db_file}")
        except Exception as e:
            self.logger.error(f"Error saving to SQLite: {e}")
    
    def export_to_markdown(self, articles: List[Dict], filename: str):
        """Export articles to Markdown report"""
        if not articles:
            self.logger.warning("No articles to export")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as md_file:
                # Write header
                keyword = articles[0]['keyword'] if articles else 'Unknown'
                md_file.write(f"# Google News Report: {keyword}\n\n")
                md_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                md_file.write(f"Total articles: {len(articles)}\n\n")
                
                # Write articles
                for i, article in enumerate(articles, 1):
                    md_file.write(f"## Article {i}: {article['title']}\n\n")
                    md_file.write(f"- **URL**: {article['url']}\n")
                    md_file.write(f"- **Published**: {article['date_published'] or 'Unknown'}\n")
                    md_file.write(f"- **Scraped**: {article['scraped_at']}\n")
                    md_file.write(f"- **Snippet**: {article['snippet']}\n\n")
                    md_file.write("---\n\n")
            
            self.logger.info(f"Exported report to {filename}")
        except Exception as e:
            self.logger.error(f"Error exporting to Markdown: {e}")
    
    def export_to_html(self, articles: List[Dict], filename: str):
        """Export articles to HTML report"""
        if not articles:
            self.logger.warning("No articles to export")
            return
        
        try:
            # HTML template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Google News Report: {{ keyword }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    h1 { color: #333; }
                    .article { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
                    .article h2 { margin-top: 0; }
                    .meta { color: #666; font-size: 0.9em; }
                    .snippet { margin-top: 10px; }
                </style>
            </head>
            <body>
                <h1>Google News Report: {{ keyword }}</h1>
                <p>Generated on: {{ generated_at }}</p>
                <p>Total articles: {{ article_count }}</p>
                
                {% for article in articles %}
                <div class="article">
                    <h2><a href="{{ article.url }}">{{ article.title }}</a></h2>
                    <div class="meta">
                        <strong>Published:</strong> {{ article.date_published or 'Unknown' }} | 
                        <strong>Scraped:</strong> {{ article.scraped_at }}
                    </div>
                    <div class="snippet">
                        {{ article.snippet }}
                    </div>
                </div>
                {% endfor %}
            </body>
            </html>
            """
            
            keyword = articles[0]['keyword'] if articles else 'Unknown'
            template = Template(html_template)
            html_content = template.render(
                keyword=keyword,
                generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                article_count=len(articles),
                articles=articles
            )
            
            with open(filename, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
            
            self.logger.info(f"Exported report to {filename}")
        except Exception as e:
            self.logger.error(f"Error exporting to HTML: {e}")

def load_proxies_from_file(file_path: str) -> List[str]:
    """Load proxy list from file"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Error loading proxies: {e}")
        return []

def load_user_agents_from_file(file_path: str) -> List[str]:
    """Load user agents from file"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Error loading user agents: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Google News Scraper CLI')
    parser.add_argument('keywords', nargs='+', help='Keywords to search for')
    parser.add_argument('--max-articles', type=int, default=10, help='Maximum articles per keyword (default: 10)')
    parser.add_argument('--output-format', choices=['csv', 'json', 'sqlite', 'all'], default='csv', 
                       help='Output format (default: csv)')
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--report-format', choices=['markdown', 'html', 'both'], help='Generate report in specified format')
    parser.add_argument('--proxy-file', help='File containing list of proxies (one per line)')
    parser.add_argument('--user-agent-file', help='File containing list of user agents (one per line)')
    parser.add_argument('--domain-filter', help='Filter results by domain (e.g., bbc.com)')
    parser.add_argument('--schedule', help='Run on schedule (e.g., "1h" for hourly, "30m" for every 30 minutes)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(exist_ok=True)
    
    # Load proxies and user agents if provided
    proxies = load_proxies_from_file(args.proxy_file) if args.proxy_file else []
    user_agents = load_user_agents_from_file(args.user_agent_file) if args.user_agent_file else []
    
    # Initialize scraper
    scraper = GoogleNewsScraper(verbose=args.verbose, proxy_list=proxies, user_agents=user_agents)
    
    def run_scrape():
        """Function to run the scraping process"""
        all_articles = []
        
        for keyword in args.keywords:
            try:
                articles = scraper.scrape_articles(
                    keyword, 
                    max_articles=args.max_articles,
                    domain_filter=args.domain_filter
                )
                all_articles.extend(articles)
                
                # Save results
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_keyword = re.sub(r'[^\w\-_]', '_', keyword)
                
                if args.output_format in ['csv', 'all']:
                    csv_file = Path(args.output_dir) / f"news_{safe_keyword}_{timestamp}.csv"
                    scraper.save_to_csv(articles, str(csv_file))
                
                if args.output_format in ['json', 'all']:
                    json_file = Path(args.output_dir) / f"news_{safe_keyword}_{timestamp}.json"
                    scraper.save_to_json(articles, str(json_file))
                
                if args.output_format in ['sqlite', 'all']:
                    db_file = Path(args.output_dir) / f"news_{timestamp}.db"
                    scraper.save_to_sqlite(articles, str(db_file))
                
                # Generate reports
                if args.report_format in ['markdown', 'both']:
                    md_file = Path(args.output_dir) / f"report_{safe_keyword}_{timestamp}.md"
                    scraper.export_to_markdown(articles, str(md_file))
                
                if args.report_format in ['html', 'both']:
                    html_file = Path(args.output_dir) / f"report_{safe_keyword}_{timestamp}.html"
                    scraper.export_to_html(articles, str(html_file))
                    
            except Exception as e:
                scraper.logger.error(f"Error processing keyword '{keyword}': {e}")
                continue
        
        return all_articles
    
    # Run based on schedule or once
    if args.schedule:
        scraper.logger.info(f"Scheduling scraper to run every {args.schedule}")
        
        # Parse schedule interval
        interval = args.schedule.lower()
        if interval.endswith('h'):
            hours = int(interval[:-1])
            schedule.every(hours).hours.do(run_scrape)
        elif interval.endswith('m'):
            minutes = int(interval[:-1])
            schedule.every(minutes).minutes.do(run_scrape)
        else:
            scraper.logger.error("Invalid schedule format. Use like '1h' or '30m'")
            return
        
        # Run first immediately
        run_scrape()
        
        # Keep running scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # Run once
        run_scrape()

if __name__ == "__main__":
    main()

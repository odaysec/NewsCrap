# NewsCrap
NewsCrap adalah alat scraping berita Google berbasis Command Line Interface (CLI) yang dirancang untuk riset, investigasi, dan pengumpulan data OSINT. Dengan fitur canggih seperti rotation proxy, scheduling otomatis, dan multi-format export, alat ini memudahkan pengumpulan data berita secara efisien dan andal.


![CLI](https://img.shields.io/badge/CLI-Tool-green)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![OSINT](https://img.shields.io/badge/OSINT-Tool-orange)

## Fitur Utama

- **Multi-keyword Support** - Cari dengan beberapa keyword sekaligus
- **Pagination Scraping** - Ambil artikel dari banyak halaman hasil
- **Multi-format Export** - CSV, JSON, SQLite database
- **Proxy & User-Agent Rotation** - Hindari deteksi dan blokir
- **Scheduler Mode** - Jalankan otomatis sesuai interval waktu
- **Deduplication & Filtering** - Hindari duplikat dan filter by domain
- **Report Generation** - Export laporan Markdown/HTML
- **Verbose Logging** - Pantau proses scraping secara detail
- **Error Handling** - Tetap berjalan meski ada error

## Instalasi

1. **Clone Repository**
```bash
git clone https://github.com/opsysdebug/NewsCrap.git
cd NewsCrap
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```


```bash
# Scrape berita dengan keyword tunggal
python news_scrap.py "artificial intelligence"

# Multiple keywords
python news_scrap.py "AI" "machine learning" "deep learning"

# Dengan batasan jumlah artikel
python news_scrap.py "cybersecurity" --max-articles 50
```

```bash
# Export ke JSON dengan filter domain
python news_scrap.py "technology" --output-format json --domain-filter bbc.com

# Dengan proxy rotation dan user agent
python news_scrap.py "news" --proxy-file proxies.txt --user-agent-file user_agents.txt

# Mode terjadwal (setiap 2 jam)
python news_scrap.py "cryptocurrency" --schedule 2h --verbose

# Generate laporan HTML
python news_scrap.py "politics" --report-format html --max-articles 30
```


```bash
usage: news_scrap.py [-h] [--max-articles MAX_ARTICLES] [--output-format {csv,json,sqlite,all}]
                    [--output-dir OUTPUT_DIR] [--report-format {markdown,html,both}]
                    [--proxy-file PROXY_FILE] [--user-agent-file USER_AGENT_FILE]
                    [--domain-filter DOMAIN_FILTER] [--schedule SCHEDULE] [--verbose]
                    keywords [keywords ...]

Google News Scraper CLI

positional arguments:
  keywords              Keywords to search for

optional arguments:
  -h, --help            show this help message and exit
  --max-articles MAX_ARTICLES
                        Maximum articles per keyword (default: 10)
  --output-format {csv,json,sqlite,all}
                        Output format (default: csv)
  --output-dir OUTPUT_DIR
                        Output directory (default: output)
  --report-format {markdown,html,both}
                        Generate report in specified format
  --proxy-file PROXY_FILE
                        File containing list of proxies (one per line)
  --user-agent-file USER_AGENT_FILE
                        File containing list of user agents (one per line)
  --domain-filter DOMAIN_FILTER
                        Filter results by domain (e.g., bbc.com)
  --schedule SCHEDULE   Run on schedule (e.g., "1h" for hourly, "30m" for every 30 minutes)
  --verbose, -v         Verbose output
```

---

## File Konfigurasi
### proxies.txt
```
http://proxy1.example.com:8080
http://proxy2.example.com:3128
socks5://proxy3.example.com:1080
```

### user_agents.txt
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
```

## Penggunaan CLI
### Untuk Riset Akademik
```bash
python news_scrap.py "climate change" "global warming" --max-articles 100 --output-format json
```

### Untuk Investigasi OSINT
```bash
python news_scrap.py "company name" --domain-filter reuters.com --proxy-file proxies.txt --schedule 6h
```

### Untuk Monitoring Berita
```bash
python news_scrap.py "breaking news" --schedule 30m --report-format both --verbose
```

## Penting
- Gunakan tool ini secara bertanggung jawab dan patuhi Terms of Service Google
- Respect robots.txt dan rate limiting
- Disarankan menggunakan proxy untuk menghindari IP blocking
- Tool ini untuk tujuan edukasi dan research yang legal

### Troubleshooting
**Error: 429 Too Many Requests** (gunakan proxy jangan lupa)
```bash
python news_scrap.py "keyword" --proxy-file proxies.txt
```

**Error: Connection Issues**
```bash
# Pastikan koneksi internet stabil
# Coba dengan user agent berbeda
```



## ⭐ Support

Your sponsor akan sangat berharga bagi saya dalam research project maupun aktifitas saya di OSS lebih lanjut. terimakasih banyak.
---

**Disclaimer**: Tool ini dibuat untuk tujuan edukasi dan research. Pengguna bertanggung jawab penuh atas penggunaan tool ini sesuai dengan hukum yang berlaku dan kebijakan website yang di-scrape.

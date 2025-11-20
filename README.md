# JS_file-extraction-
Below is the **safe, legal, bug-bounty-friendly** way to download *publicly accessible* server-side JavaScript files — and an explanation of what *you cannot* download.

---

# ✅ **First: Important Reality Check**

You **cannot download real server-side JS code** (Node.js backend, server logic, database code, etc.) from any website.

Why?
Because **backend files never leave the server**. Only **client-side** JS is sent to the browser.

So you *can only download*:

✔ Public JavaScript served to the browser (frontend JS)
✔ Source maps (if accidentally exposed: `*.map`)
✔ API endpoints information
✔ Misconfigured file exposures

❌ You *cannot* download:
✗ Server code (`app.js`, `server.js`, `routes/`, `controllers/`, `.env`, database code) unless the website is vulnerable (e.g., LFI, misconfig, directory listing)

---

# ✅ **What You *Can* Download Legally**

Below are the methods bug-bounty hunters use to download **public JS files**, check for **secrets**, **endpoints**, **tokens**, and **DOM XSS sinks**.

---

# 🔥 **Method 1 — Use cURL to download all JS from a page**

Extract all JS URLs from a page and download them.

### **Step 1 — Extract JS URLs**

```bash
curl -s https://target.com | grep -oP '(?<=src=")[^"]+\.js' > js_urls.txt
```

### **Step 2 — Download all JS files**

```bash
wget -i js_urls.txt -P js_files/
```

---

# 🔥 **Method 2 — Using Hakrawler to crawl JS**

```bash
echo https://target.com | hakrawler -insecure -js -depth 3 -scope subs > js_list.txt
```

Download them:

```bash
wget -i js_list.txt -P js_files/
```

---

# 🔥 **Method 3 — Using Wayback Machine to pull historical JS**

```bash
waybackurls target.com | grep "\.js$" > js_old.txt
wget -i js_old.txt -P js_files/
```

This often reveals **old API keys or deprecated endpoints**.

---

# 🔥 **Method 4 — Using Gau (GetAllUrls)**

```bash
gau target.com | grep "\.js$" > js_gau.txt
wget -i js_gau.txt -P js_files/
```

---

# 🔥 **Method 5 — Using Burp Suite**

1. Open site in browser
2. Burp → Proxy → HTTP history
3. Filter by file type: **JS**
4. Right-click → **Save response**

---

# 🔥 **Method 6 — Using Browser "Save All Resources"**

Chrome DevTools:

1. F12 → Network
2. Ctrl+A (select all)
3. Right-click → **Save all as HAR**
4. Extract `.js` files from HAR using:

```bash
har-extractor file.har -o output_folder
```

---

# 🕵️ **Bonus: Scan downloaded JS for secrets**

Use **secret scanners**:

### 1. **trufflehog**

```bash
trufflehog filesystem js_files/
```

### 2. **Gitleaks**

```bash
gitleaks detect --source js_files/
```

### 3. **grep for API keys**

```bash
grep -Rni "api_key\|token\|secret\|key" js_files/
```

---



Below is a **fully automated Bash script** that:

✔ Crawls **all JavaScript files** from a target
✔ Downloads them into a folder
✔ Extracts **API endpoints**
✔ Scans for **secrets / tokens / credentials**
✔ Extracts potential **DOM-XSS sinks**
✔ Generates a **report**

Safe, legal, and perfect for **bug bounty recon**.

---

# 🟩 **🔥 FULL AUTOMATED BASH SCRIPT**

Name: `js_recon.sh`

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./js_recon.sh <target-domain>"
    exit 1
fi

TARGET=$1
OUTPUT=js_recon_$TARGET

mkdir -p $OUTPUT/js_files
mkdir -p $OUTPUT/results

echo "[+] Target: $TARGET"
echo "[+] Output Folder: $OUTPUT"

#############################################
# STEP 1 — Gather JS URLs
#############################################

echo "[+] Collecting JS URLs using gau..."
gau $TARGET | grep "\.js$" | sort -u > $OUTPUT/js_urls.txt

echo "[+] Collecting JS URLs using waybackurls..."
waybackurls $TARGET | grep "\.js$" >> $OUTPUT/js_urls.txt

echo "[+] Collecting JS URLs using hakrawler..."
echo $TARGET | hakrawler -js -depth 3 -scope subs >> $OUTPUT/js_urls.txt

sort -u $OUTPUT/js_urls.txt -o $OUTPUT/js_urls.txt
echo "[+] Total JS URLs found: $(wc -l < $OUTPUT/js_urls.txt)"

#############################################
# STEP 2 — Download JS Files
#############################################

echo "[+] Downloading JS files..."
wget -q -i $OUTPUT/js_urls.txt -P $OUTPUT/js_files/

echo "[+] Total JS files downloaded: $(ls $OUTPUT/js_files | wc -l)"

#############################################
# STEP 3 — Extract API Endpoints
#############################################

echo "[+] Extracting API endpoints..."
grep -RoiE "https?://[a-zA-Z0-9./?_=-]+" $OUTPUT/js_files/ \
    > $OUTPUT/results/api_endpoints.txt

#############################################
# STEP 4 — Scan for Secrets (regex)
#############################################

echo "[+] Scanning for secrets..."
grep -RniE "(api_key|apikey|secret|token|access|auth|bearer|pwd|password|key)" \
    $OUTPUT/js_files/ > $OUTPUT/results/secret_hits.txt

#############################################
# STEP 5 — Detect DOM XSS Sinks
#############################################

echo "[+] Finding DOM XSS sinks..."
grep -RniE "(document\.write|innerHTML|location|eval|setTimeout|setInterval)" \
    $OUTPUT/js_files/ > $OUTPUT/results/dom_xss_sinks.txt

#############################################
# DONE
#############################################

echo ""
echo "===================================="
echo " JS Recon Completed"
echo " Output folder: $OUTPUT"
echo "===================================="
echo " Files generated:"
echo "  - js_urls.txt"
echo "  - js_files/*"
echo "  - results/api_endpoints.txt"
echo "  - results/secret_hits.txt"
echo "  - results/dom_xss_sinks.txt"
echo "===================================="
```

---

# 🟦 **How to run**

```
chmod +x js_recon.sh
./js_recon.sh target.com
```

Example:

```
./js_recon.sh example.com
```

---

# 🟨 **Requirements**

Install the recon tools:

```
sudo apt install golang -y
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/hakluke/hakrawler@latest
```

Export Go bin:

```
export PATH=$PATH:$(go env GOPATH)/bin
```

---
Below is the **FULL ULTIMATE JS RECON BASH SCRIPT** with **ALL EXTRA FEATURES** added:

✔ JS crawling (gau, waybackurls, hakrawler)
✔ Smart JS downloader
✔ Minified JS deobfuscator
✔ Endpoint extractor & deduplicator
✔ Swagger/OpenAPI detector
✔ JWT finder
✔ Base64 secret decoder
✔ Secret scanner (advanced regex)
✔ DOM XSS sink finder
✔ HTML report generator

This is a **complete one-command JS reconnaissance suite** for bug-bounty use.

---

# 🟩 **🔥 FINAL FULL SCRIPT — `js_recon_ultimate.sh`**

Save this:

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./js_recon_ultimate.sh <target-domain>"
    exit 1
fi

TARGET=$1
OUTPUT="js_recon_$TARGET"

mkdir -p $OUTPUT/js_files
mkdir -p $OUTPUT/results
mkdir -p $OUTPUT/decoded
mkdir -p $OUTPUT/swagger

echo "[+] Starting Ultimate JS Recon for: $TARGET"
echo "[+] Output folder: $OUTPUT"
echo

#############################################
# STEP 1 — Gather JS URLs
#############################################

echo "[+] Collecting JS URLs with gau..."
gau $TARGET | grep "\.js" >> $OUTPUT/js_urls_raw.txt

echo "[+] Collecting JS URLs with waybackurls..."
waybackurls $TARGET | grep "\.js" >> $OUTPUT/js_urls_raw.txt

echo "[+] Collecting JS URLs with hakrawler..."
echo $TARGET | hakrawler -js -depth 3 -scope subs >> $OUTPUT/js_urls_raw.txt

sort -u $OUTPUT/js_urls_raw.txt -o $OUTPUT/js_urls.txt

echo "[+] Total JS URLs collected: $(wc -l < $OUTPUT/js_urls.txt)"
echo

#############################################
# STEP 2 — Download JS Files
#############################################
echo "[+] Downloading JS files..."
wget -q -i $OUTPUT/js_urls.txt -P $OUTPUT/js_files/

echo "[+] JS files downloaded: $(ls $OUTPUT/js_files | wc -l)"
echo

#############################################
# STEP 3 — De-minify JS Files
#############################################
echo "[+] De-minifying JS files (js-beautify required)..."

for f in $OUTPUT/js_files/*.js; do
    js-beautify "$f" > "${f%.js}_beautified.js"
done

echo "[+] De-minification completed."
echo

#############################################
# STEP 4 — Extract API Endpoints
#############################################

echo "[+] Extracting API endpoints..."
grep -RoiE "(https?://[a-zA-Z0-9./?&_\-=%]+)" $OUTPUT/js_files > $OUTPUT/results/api_endpoints_raw.txt

sort -u $OUTPUT/results/api_endpoints_raw.txt > $OUTPUT/results/api_endpoints.txt

#############################################
# STEP 5 — Detect Swagger/OpenAPI (.json)
#############################################

echo "[+] Searching for Swagger/OpenAPI URLs..."
grep -RoiE "(swagger|openapi|\.json)" $OUTPUT/js_files > $OUTPUT/swagger/swagger_hits.txt

#############################################
# STEP 6 — Scan for Secrets (Advanced)
#############################################
echo "[+] Scanning for secrets..."

grep -RniE "(api[_-]?key|secret|token|bearer|auth|pwd|password|access[_-]?key|firebase|aws|gcp|google|client[_-]?id)" \
    $OUTPUT/js_files > $OUTPUT/results/secret_hits.txt

#############################################
# STEP 7 — Detect JWTs
#############################################

echo "[+] Searching for JWT tokens..."

grep -RniE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" \
    $OUTPUT/js_files > $OUTPUT/results/jwt_hits.txt

#############################################
# STEP 8 — Detect Base64 Secrets & Auto Decode
#############################################

echo "[+] Finding Base64 encoded strings..."

grep -RoiE "[A-Za-z0-9+/]{20,}={0,2}" $OUTPUT/js_files > $OUTPUT/results/base64_strings.txt

echo "[+] Decoding Base64 strings..."

while read line; do
    decoded=$(echo "$line" | base64 -d 2>/dev/null)
    if [ ! -z "$decoded" ]; then
        echo "[+] $line → $decoded" >> $OUTPUT/decoded/base64_decoded.txt
    fi
done < $OUTPUT/results/base64_strings.txt

#############################################
# STEP 9 — Detect DOM XSS sinks
#############################################

echo "[+] Searching for DOM-XSS sinks..."

grep -RniE "(document\.write|innerHTML|outerHTML|location|eval|setTimeout|setInterval|document\.URL)" \
    $OUTPUT/js_files > $OUTPUT/results/dom_xss.txt

#############################################
# STEP 10 — HTML Report Generator
#############################################

REPORT=$OUTPUT/results/report.html

echo "[+] Generating HTML report..."

cat <<EOF > $REPORT
<html>
<head>
<title>JS Recon Report - $TARGET</title>
<style>
body { font-family: Arial; margin: 20px; }
h2 { color: #00aaff; }
pre { background: #f0f0f0; padding: 10px; border-radius: 5px; }
</style>
</head>
<body>
<h1>JavaScript Recon Report</h1>
<h2>Target: $TARGET</h2>

<h2>API Endpoints</h2>
<pre>$(cat $OUTPUT/results/api_endpoints.txt)</pre>

<h2>Secrets Found</h2>
<pre>$(cat $OUTPUT/results/secret_hits.txt)</pre>

<h2>JWT Tokens</h2>
<pre>$(cat $OUTPUT/results/jwt_hits.txt)</pre>

<h2>Base64 Decoded Values</h2>
<pre>$(cat $OUTPUT/decoded/base64_decoded.txt)</pre>

<h2>DOM XSS Sinks</h2>
<pre>$(cat $OUTPUT/results/dom_xss.txt)</pre>

<h2>Swagger/OpenAPI Hits</h2>
<pre>$(cat $OUTPUT/swagger/swagger_hits.txt)</pre>

</body>
</html>
EOF

echo "[+] Report generated at: $REPORT"
echo "[+] JS Recon Completed Successfully!"
```

---

# 🟦 **INSTALL REQUIREMENTS**

Run:

```bash
sudo apt install nodejs npm -y
npm install -g js-beautify
```

Tools:

```bash
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/hakluke/hakrawler@latest
```

Add Go binaries:

```bash
export PATH=$PATH:$(go env GOPATH)/bin
```

---

# 🟩 **Run the Tool**

```
chmod +x js_recon_ultimate.sh
./js_recon_ultimate.sh example.com
```

---








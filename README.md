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
## Usage Examples:

```bash
# BIG Mode (secrets + endpoints)
python3 mega_js_scanner.py --mode big --jsdir /path/to/js/files

# DEEP Mode (AST analysis)
python3 mega_js_scanner.py --mode deep --jsdir /path/to/js/files

# DOM Mode (DOM-XSS detection)
python3 mega_js_scanner.py --mode dom --jsdir /path/to/js/files

# PROFESSIONAL Mode (all scans)
python3 mega_js_scanner.py --mode professional --jsdir /path/to/js/files

# GAU Mode (fetch JS from domain)
python3 mega_js_scanner.py --mode gau --target example.com
```

## Required Dependencies:

```bash
pip3 install colorama tqdm aiohttp esprima
```

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
Here is exactly **what to do next** after you generate **dom_xss.txt** from your JavaScript recon.

Your file usually contains things like:

* `document.location`
* `location.hash`
* `document.URL`
* `window.name`
* `innerHTML`
* `eval()`
* `setTimeout(string)`
* `unsafe sink lines`

Now the next step is **confirming whether the DOM XSS is exploitable**.

---

# ✅ **STEP-BY-STEP: What to do after getting `dom_xss.txt`**

---

# **1️⃣ Identify the JS file & line number**

Your dom_xss.txt usually has path or filename.

Example:

```
/js/app/main.js:1223:  document.location
/js/app/cart.js:55:    innerHTML = q
```

→ You need to **open those JS files** and inspect code.

---

# **2️⃣ Find the source → sink flow**

DOM XSS requires:

```
User-controlled input (source)
        ↓
Executed in dangerous function (sink)
```

### Common Sources

```
location
location.hash
location.search
document.URL
document.referrer
window.name
```

### Common Sinks

```
innerHTML
outerHTML
document.write
eval
setTimeout(string)
insertAdjacentHTML
Function()
```

If the source is directly used with the sink → **high chance it's exploitable.**

---

# **3️⃣ Try payloads for that specific flow**

### Example 1

Code:

```js
var q = location.hash.replace('#','');
document.getElementById("output").innerHTML = q;
```

This is **vulnerable**.

Test in browser:

```
https://example.com/page#<img src=x onerror=alert(1)>
```

If popup appears → DOM XSS confirmed.

---

### Example 2

Code:

```js
var id = new URLSearchParams(location.search).get("id");
document.write(id);
```

Payload:

```
https://example.com/product?id=<svg/onload=alert(1)>
```

---

# **4️⃣ Test using DOM Invader (BurpSuite)**

If you have BurpSuite installed:

Burp → Tools → DOM Invader → Enable

Then visit the page → it automatically:

* Traces the source → sink flow
* Finds taint-tracking
* Tells whether vulnerable
* Provides exploit payloads

This is the **most accurate method**.

---

# **5️⃣ Check indirect sinks (stored in variables)**

Example:

```js
let x = location.search.slice(1);
someElement.innerHTML = process(x);
```

Even if sanitization exists, test with:

```
"><img src=x onerror=alert(1337)>
```

---

# **6️⃣ Build POC only after confirming scope**

⚠️ Make sure the domain is allowed in bug bounty scope.

---

# **7️⃣ Write a final report only if:**

A working payload causes execution:

* alert()
* console.log()
* DOM modification
* JavaScript execution

Then include:

* URL tested
* Payload used
* JS code snippet
* Impact description
* Screenshot or recording

---










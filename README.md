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



`https://target.com/.env`
`https://target.com/package.json`



# Segan Industry Website — Enhancement Build (2026-10-17)

> ⚠️ **UNVERIFIED PUBLIC CLAIMS — confirm or remove before launch.** The site currently states, as fact:
> - **"Founded in 2009"** / "Over 15 years" (about.html) — company launches Feb 2027
> - **"ISO 9001:2015 Certified"** and **"IATF 16949 In Progress"** (index hero badge, about.html, index features) — certifications not held yet per founder
> - **"Serving automotive OEMs, EV startups, and industrial automation companies"** (about.html)
> Per founder instruction these were **NOT edited** — but leaving them public means the live site makes claims a prospect could rely on. Confirm/remove.
>
> ⚠️ **GSTIN is a sample value:** `CONFIG.gstin = '33AAECS1234F1Z5'` in app.js. It is no longer displayed anywhere on the site (quote info panel now shows "GSTIN: —"), but do not treat it as the company's real GSTIN. **Founder will supply the real GST number later.**

Source: live copies of https://segan-industry-website.vercel.app/ (downloaded 2026-10-17).
Folder: `~/workspace/segan-website-enhanced/` — drop into the website Git repo (commit → Vercel redeploys automatically).

## 1. Logo (new S/H cable logo) — all 6 pages
- `<head>`: old `<link rel="icon" href="assets/logo.svg">` replaced with `assets/favicon-32.png` + `assets/favicon-64.png` (PNG favicons), apple-touch-icon → `assets/apple-touch-icon.png`. This also fixes the **404 on `assets/logo.png`** (only index.html referenced it as apple-touch-icon; it never existed on the live site).
- Header: `<div class="nav-logo">SI</div>` badge → `<img src="assets/logo-nav.png" class="nav-logo-img">` (~44px, rounded).
- Footer: `.footer-logo` SI badge → same logo-nav image (footer-logo-img class).
- index.html hero: `assets/logo-wide.png` above the H1 (max-width 400px, rounded, navy bg + electric-blue/gold glow).
- Open Graph: `og:title` / `og:description` / `og:type` / `og:image` → `assets/logo-icon-512.png`; added `theme-color #010315`. (The old `og:image` pointed to `assets/images/og-image.jpg` which **never existed** — fixed.)
- New files in `assets/`: logo-nav.png, logo-wide.png, logo-icon-192.png, logo-icon-512.png, favicon-32.png, favicon-64.png, apple-touch-icon.png.
- **Safe to delete from the repo:** `assets/logo.svg` (old metallic "SI" logo) once this ships — nothing references it anymore. `assets/logo.png` was never there.

## 2. Dead Railway API — the big finding
`app.js` pointed every dynamic feature at `https://segan-industry-website-production.up.railway.app/api`. Verified 2026-10-17: **Railway returns 404 "Application not found" for EVERY endpoint** — the backend is gone. So on the live site today:
- ❌ Contact form always fails ("Failed to send message")
- ❌ Quote/AI quote generator always fails
- ❌ Chat widget always fails ("Sorry, I encountered an error")
- ❌ Product-detail page (`products.html?id=...`) shows a stuck error (its selector `.quote-result` doesn't even exist on quote.html)
- Products + automation pages only worked because of static fallbacks

### Fixes applied (app.js)
- `CONFIG.apiBaseUrl` removed; legacy `api.request()` now fails fast into the existing static fallbacks — no spinners stuck, no console rejections.
- Loader catches no longer show fake "Failed to load…" error toasts; static fallbacks are the normal path.
- **Chat widget → NEW public endpoint**: `POST https://seganindustry.duckdns.org/api/v1/website/chat` with `{message, session_id}` → reads `{reply}` (session_id kept across the chat). **Important: the widget does NOT call `/api/v1/agent/*`** — those need a Bearer token and their CORS does not allow the website origin, so they'd 401/fail in a browser. Typing indicator while waiting; chat history stays in the panel during the session; Enter-to-send kept. On failure: friendly fallback offering email + contact page. Quick-reply starter chips ("What products do you make?", "How do I get a quote?", "Where are you located?") send on click and hide after the visitor's first message. Chat header already names the assistant **"Segan AI Assistant"**. (If the new `/website/chat` endpoint isn't deployed yet, the widget degrades to the contact fallback — no dead spinners.)
- Replies are HTML-escaped with line breaks preserved before rendering.
- **Contact form → POST first, mailto fallback**: `POST` JSON `{name,email,phone,company,contact_type,subject,message}` to `/api/v1/website/contact`. Success → "Message received! We will get back to you shortly." Failure → opens the email app (mailto `info@seganindustry.com`) with honest wording (never claims "sent").
- **Quote page → RFQ flow with backend capture**: validates client-side, `POST`s ALL form fields as JSON to `/api/v1/website/quote`. Success → renders the RFQ summary + "Request received! Our team will contact you shortly." (+ reference id if the response includes one). Failure → still renders the summary AND opens the email app (mailto `sales@seganindustry.com`) so the enquiry is never lost. **No pricing** — no fake prices anywhere.
- **Enquiry capture:** every quote request, contact message and chat conversation is captured to the founder's system through these public endpoints (chat sends a per-page-load `session_id` in every message body for the conversation log) — the founder can be notified from these submissions on the backend side. Page copy de-marketing'ed: "AI Quote Generator" → "Request a Quote", "AI Powered" → "RFQ", "AI Calculates Instantly" → "We Respond with a Quotation", meta description updated.
- **"PDF download coming soon!"** → real "Print / Save as PDF" (`window.print()`).
- **"Detailed view coming soon!"** (automation Learn More) → inline expand/collapse showing the service's included features + technologies (data already existed on the card) with a "Request a Quote for this service" link to quote.html.
- Product-detail page now resolves from the static catalog (shared `getStaticProducts()`); unknown id → friendly "Product not found" + back link.

## 3. Dead links — all resolved
Every page had 6 `href="#"`: 3 social icons + 3 footer-legal. Now:
- LinkedIn / Twitter / YouTube icons → `contact.html` (social URLs unknown — kept the icons per spec)
- Privacy Policy / Terms of Service → `about.html`; GST Compliance → `contact.html`
- **No `href="#"` remains** anywhere (the only `#`-starting selector in app.js is the smooth-scroll handler for real anchor links — that one works and was kept).

## 4. Design refresh (enhancement layer appended to END of style.css — original untouched)
- Navy (#010315) logo glow on hero (electric blue + gold)
- Card hover: lift + accent border + glow; button hover lift/active states
- `:focus-visible` outlines (a11y)
- Section spacing polish; RFQ summary/print stylesheet polish (chat widget + action buttons hidden on print)

## 5. Flagged items — NOT changed (founder will update later)
- **Address + GST number**: founder said he will update these himself in future — left exactly as-is everywhere (footers, contact page, about page, `CONFIG.gstin` in app.js).
- Phone numbers displayed are placeholder-looking: **+91 44 2625 1234** and **+91 98765 43210** (also in tel: links) — left as-is per founder.
- Emails `info@seganindustry.com` / `sales@seganindustry.com` are used in mailto flows; not verified as real inboxes — confirm before relying on them.
- GSTIN `33AAECS1234F1Z5` appears in `CONFIG.gstin` (app.js) — left as-is; founder will update.

## 6. Verification (2026-10-17, local server)
- `node --check app.js` → syntax OK
- Served the folder with `python3 -m http.server`; every page + every new asset → HTTP 200
- `grep railway app.js` → only in a code comment, no live URL
- `grep 'href="#"'` over all pages → zero matches
- Section/headline diff vs the original live copies → all original sections present

## 7. What to do with this
1. Copy the 6 `.html` files, `style.css`, `app.js`, and the `assets/` folder over the website Git repo folder (on Windows: `C:\VS code AI project\Segan Industry\Segan Industry Website\`).
2. Delete `assets/logo.svg` from the repo (old logo, now unreferenced).
3. Commit + push → Vercel redeploys automatically.
4. Sanity-check the live site: favicon shows the new logo, chat answers a question, contact/quote buttons open your email app, quote "Print / Save as PDF" opens the print dialog.

## 8. UPDATE #3 — audit bug fixes (2026-10-17)
- **Contact form crash fixed:** contact.html has no `.form-message` element and the old handler touched it outside try/catch → TypeError on every submit. The handler now creates the status div if missing (null-guarded).
- **Contact field mapping fixed:** the form's real fields are `firstName`/`lastName`/`inquiryType` (the old JS read `name`/`contact_type`/`subject`, so submissions were empty). Now: `name = firstName + lastName`, `contact_type = inquiryType`, `subject = inquiryType`. Payload keys stay `{name,email,phone,company,contact_type,subject,message}`. Quote handler checked — no such pattern.
- **Product catalog:** static fallback expanded to 11 generic products across Automotive / EV / Industrial / Components / Custom — no prices, no invented specs or certifications. Renderers only show price/MOQ/lead-time when present; each product card now has a "Request Quote" button linking to quote.html?product=ID.
- **SEO basics added:** `robots.txt` (allow all + sitemap line) and `sitemap.xml` (6 pages) at the site root.
- **Footer copyright:** © 2024 → © 2026 on all 6 pages.
- **Chat window mobile:** fixed 380px width overflowed small phones — added `max-width:480px` media query (width `calc(100vw - 24px)`, right 12px) in the enhancement layer.
- **GSTIN display:** the sample value was shown in the quote page info panel — replaced with "GSTIN: —". The `CONFIG.gstin` sample remains in code but is never rendered.

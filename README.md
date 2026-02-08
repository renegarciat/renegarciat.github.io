# CV Starter — simple static site

This is a small static site you can edit to build your CV/resume.

Files added
- `index.html` — main page to edit (open in a browser to preview)
- `css/styles.css` — simple styling
- `js/script.js` — small interactions (mobile nav, copy email)

Quick preview

Option A — open directly (simple):

```bash
xdg-open index.html
```

Option B — run a tiny static server (recommended for consistent relative paths):

```bash
# from the project folder
python3 -m http.server 8000
# then open http://localhost:8000 in your browser
```

Export to PDF

- Open `index.html` in the browser and use Print -> Save as PDF. Use A4 or Letter and "Scale: 100%" for best results.
- For automated conversion with styling preserved, install `wkhtmltopdf` or use `pandoc` with a CSS file.

Deploy options

- GitHub Pages: commit this folder to a repo and enable Pages (branch `main` or `gh-pages`).
- Netlify / Vercel: both detect static sites and deploy with zero config — connect your repo and push.

Next steps I can help with

- Add your personal content (I can fill sections if you give me text)
- Improve typography and print styles for PDF
- Add a downloadable `cv.pdf` and social links
- Set up a GitHub repository and automatic deploy to GitHub Pages

Tell me what you'd like to do next and I will continue.

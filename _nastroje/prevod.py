"""Převede HTML návrhu (jak ho vrací Artifact read) na samostatnou veřejnou stránku.
Použití: python3 _nastroje/prevod.py vstup.html slozka-firmy
Vytvoří slozka-firmy/index.html s úplnou hlavičkou (lang, title, description, noindex).
"""
import re, sys, pathlib

src, slug = sys.argv[1], sys.argv[2]
html = pathlib.Path(src).read_text(encoding="utf-8")
m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
body = m.group(1) if m else html
head_parts = []
for pat in (r"<title>.*?</title>", r"<meta name=\"description\"[^>]*>",
            r"<meta name=\"robots\"[^>]*>", r"<link rel=\"stylesheet\"[^>]*>",
            r"<script type=\"application/ld\+json\">.*?</script>"):
    for hit in re.findall(pat, body, re.S):
        head_parts.append(hit)
        body = body.replace(hit, "", 1)
if not any("robots" in h for h in head_parts):
    head_parts.append('<meta name="robots" content="noindex,nofollow">')
page = ("<!doctype html>\n<html lang=\"cs\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
        + "\n".join(head_parts) +
        "\n<style>html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;"
        "font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}"
        "img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>\n"
        "</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n")
out = pathlib.Path(slug)
out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(page, encoding="utf-8")
print("hotovo:", out / "index.html", len(page), "znaků")

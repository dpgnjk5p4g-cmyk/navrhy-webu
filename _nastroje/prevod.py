"""Převede HTML návrhu na samostatnou veřejnou stránku pro GitHub Pages.

Použití:  python3 _nastroje/prevod.py vstup.html slozka-firmy
Vytvoří:  slozka-firmy/index.html  (úplná hlavička, lang="cs", noindex)

Vstup může být celý dokument (<html><head>…<body>…), dokument, jak ho vrací
čtení artefaktu (title a meta až v <body>), nebo jen obsah stránky.
"""
import pathlib
import re
import sys

HEAD_TAGS = (
    r"<title>.*?</title>",
    r"<meta\s+name=[\"']?(?:description|robots|theme-color)[\"']?[^>]*>",
    r"<meta\s+property=[\"']og:[^>]*>",
    r"<link\s[^>]*>",
    r"<script\s+type=[\"']application/ld\+json[\"']>.*?</script>",
)


def convert(html: str) -> str:
    head_m = re.search(r"<head[^>]*>(.*?)</head>", html, re.S | re.I)
    body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
    head_src = head_m.group(1) if head_m else ""
    body = body_m.group(1) if body_m else re.sub(
        r"</?(?:html|head|body)[^>]*>|<!doctype[^>]*>", "", html, flags=re.I)

    parts = []
    for pat in HEAD_TAGS:                       # z hlavičky dokumentu
        parts += re.findall(pat, head_src, re.S | re.I)
    for pat in HEAD_TAGS:                       # a ty, které skončily v těle
        for hit in re.findall(pat, body, re.S | re.I):
            parts.append(hit)
            body = body.replace(hit, "", 1)
    # styly z hlavičky dokumentu (vlastní styly stránky) zachovat
    parts += re.findall(r"<style[^>]*>.*?</style>", head_src, re.S | re.I)

    seen, uniq = set(), []
    for p in parts:                             # bez duplicit, title jen jednou
        key = "title" if p.lower().startswith("<title") else p
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    uniq = [p for p in uniq if "robots" not in p.lower()[:40]]
    uniq.append('<meta name="robots" content="noindex,nofollow">')
    if not any(p.lower().startswith("<title") for p in uniq):
        uniq.insert(0, "<title>Návrh webu</title>")

    base = ("<style>html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;"
            "font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}"
            "img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>")
    return (
        "<!doctype html>\n<html lang=\"cs\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
        + base + "\n" + "\n".join(uniq) +
        "\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n"
    )


if __name__ == "__main__":
    src, slug = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        sys.exit("Složka musí být malými písmeny bez diakritiky, slova spojená pomlčkou.")
    page = convert(pathlib.Path(src).read_text(encoding="utf-8"))
    out = pathlib.Path(slug)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print("hotovo:", out / "index.html", len(page.encode("utf-8")), "bajtů")

#!/usr/bin/env python3
"""Generátor návrhů webů – profesionální styl (od 1. 11. 2026).

Jedna pevná, střídmá šablona; každá firma má vlastní paletu, písma, fotky a texty.
Použití: python3 build.py firmy.json /cesta/k/navrhy-webu
"""
import json, sys, html, pathlib, urllib.parse

import re
_NB = re.compile(r"(?<![\w\u00C0-\u017F])([vVzZsSkKaAiIoOuU]) ")
def E(x):
    return _NB.sub(lambda m: m.group(1) + "\u00a0", html.escape(str(x)))

def img(photo, w=1600, alt="", cls="", eager=False):
    """Fotka z Unsplash (licence Unsplash) s náhradní plochou, když se nenačte."""
    if not photo:
        return f'<div class="ph {cls}"><span>Sem přijde Vaše fotka</span></div>'
    src = f"https://images.unsplash.com/{photo}?auto=format&fit=crop&w={w}&q=80"
    load = "eager" if eager else "lazy"
    return (f'<div class="ph {cls}"><span>Sem přijde Vaše fotka</span>'
            f'<img src="{src}" alt="{E(alt)}" loading="{load}" onerror="this.remove()"></div>')

def tel_href(p):
    d = "".join(c for c in p if c.isdigit())
    if not d.startswith("420"):
        d = "420" + d
    return "tel:+" + d

def build(f):
    c = f["colors"]
    fonts = f["fonts"]
    fam = "&".join("family=" + urllib.parse.quote(x["gf"], safe=":;,@") for x in fonts)
    disp, body = fonts[0]["css"], fonts[1]["css"]
    phone = f["phone"]
    tel = tel_href(phone)
    name = f["name"]
    nav = "".join(f'<a href="#{a}">{E(b)}</a>' for a, b in f["nav"])

    trust = "".join(f'<li><strong>{E(a)}</strong><span>{E(b)}</span></li>' for a, b in f["trust"])

    def service(i, s):
        price = f'<p class="price">{E(s["price"])}</p>' if s.get("price") else ""
        return (f'<article class="svc"><span class="num">{i:02d}</span><h3>{E(s["title"])}</h3>'
                f'<p>{E(s["text"])}</p>{price}</article>')
    services = "".join(service(i + 1, s) for i, s in enumerate(f["services"]))

    about_list = "".join(f"<li>{E(x)}</li>" for x in f["about"]["points"])
    steps = "".join(f'<li><span>{i+1}</span><h3>{E(a)}</h3><p>{E(b)}</p></li>'
                    for i, (a, b) in enumerate(f["steps"]))
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in f["faq"])

    gal = f.get("gallery", [])
    gallery = ""
    if gal:
        cells = "".join(img(p, 1000, alt) for p, alt in gal)
        gallery = f'''<section class="sec gal" aria-label="Fotografie">
  <div class="wrap"><div class="gal-grid">{cells}</div>
  <p class="note">Ilustrační fotografie – na webu je nahradíme Vašimi vlastními.</p></div></section>'''

    extra = ""
    if f.get("extra"):
        x = f["extra"]
        extra = f'''<section class="sec band-soft" id="{x["id"]}"><div class="wrap split">
  <div><p class="eyebrow">{E(x["eyebrow"])}</p><h2>{E(x["title"])}</h2><p class="lead">{E(x["text"])}</p>
  <a class="btn" href="{tel}">{E(x["cta"])}</a></div>
  {img(x.get("photo"), 1200, x.get("alt",""), "tall")}</div></section>'''

    review = ""
    if f.get("rating"):
        r = f["rating"]
        review = f'''<section class="sec" aria-label="Hodnocení"><div class="wrap rev">
  <div class="score"><span class="big">{E(r["score"])}</span><span class="stars" aria-hidden="true">★★★★★</span>
  <span>z {E(r["count"])} hodnocení na <a href="{E(r["url"])}" rel="nofollow">Firmy.cz</a></span></div>
  <p class="quote">{E(r["text"])}</p></div></section>'''

    hours = ""
    if f.get("hours"):
        rows = "".join(f"<tr><th>{E(d)}</th><td>{E(t)}</td></tr>" for d, t in f["hours"])
        tag = f'<p class="tag">{E(f["hours_note"])}</p>' if f.get("hours_note") else ""
        hours = f'<h3>Otevírací doba</h3><table class="hours">{rows}</table>{tag}'
    elif f.get("hours_text"):
        hours = f'<h3>Otevírací doba</h3><p>{E(f["hours_text"])}</p>'

    addr = f["address"]
    addr_note = f'<p class="tag">{E(f["address_note"])}</p>' if f.get("address_note") else ""
    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f["map_query"])
    embed = "https://maps.google.com/maps?q=" + urllib.parse.quote(f["map_query"]) + "&z=15&output=embed"
    email = f.get("email")
    email_html = f'<p><span class="lbl">E-mail</span><a href="mailto:{E(email)}">{E(email)}</a></p>' if email else ""
    ico = f'<p><span class="lbl">IČO</span>{E(f["ico"])}</p>' if f.get("ico") else ""

    ld = {"@context": "https://schema.org", "@type": f["schema"], "name": name, "telephone": tel[4:],
          "address": {"@type": "PostalAddress", "streetAddress": f["street"], "addressLocality": f["city"],
                      "addressCountry": "CZ"}, "description": f["description"]}
    if email: ld["email"] = email
    if f.get("ico"): ld["taxID"] = f["ico"]

    hero_card = ""
    if f.get("hero_card"):
        a, b = f["hero_card"]
        hero_card = f'<div class="hcard"><strong>{E(a)}</strong><span>{E(b)}</span></div>'

    sms = f'<a class="m2" href="mailto:{E(email)}">Napsat e-mail</a>' if email else f'<a class="m2" href="#kontakt">Kontakt</a>'

    return f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Návrh webu – {E(name)}</title>
<meta name="description" content="{E(f["description"])}">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="{c["bg"]}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fam}&display=swap">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:{c["bg"]};--surface:{c["surface"]};--ink:{c["ink"]};--muted:{c["muted"]};--line:{c["line"]};
--accent:{c["accent"]};--accent-ink:{c["accent_ink"]};--soft:{c["soft"]};--dark:{c["dark"]};
--disp:{disp};--body:{body};--r:{f.get("radius","14px")}}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth;scroll-padding-top:84px}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.65 var(--body);-webkit-font-smoothing:antialiased}}
img{{max-width:100%;display:block}}a{{color:inherit}}
h1,h2,h3{{font-family:var(--disp);font-weight:{f.get("disp_weight",500)};line-height:1.12;margin:0 0 .5em;letter-spacing:{f.get("disp_track","-.01em")}}}
h1{{font-size:clamp(2.3rem,4.6vw,3.9rem)}}h2{{font-size:clamp(1.8rem,3.2vw,2.7rem)}}h3{{font-size:1.25rem}}
p{{margin:0 0 1em}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
.nb{{background:var(--soft);color:var(--muted);font:500 12.5px/1.4 var(--body);text-align:center;padding:7px 16px;border-bottom:1px solid var(--line)}}
.top{{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--line)}}
.top .wrap{{display:flex;align-items:center;gap:28px;min-height:72px}}
.logo{{text-decoration:none;display:flex;flex-direction:column;line-height:1.1;margin-right:auto}}
.logo b{{font:{f.get("disp_weight",500)} 1.45rem/1.1 var(--disp);letter-spacing:{f.get("disp_track","-.01em")}}}
.logo small{{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:3px}}
.nav{{display:flex;gap:26px;font-size:.95rem}}.nav a{{text-decoration:none;color:var(--muted)}}.nav a:hover{{color:var(--ink)}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--accent);color:var(--accent-ink);text-decoration:none;font-weight:600;font-size:.98rem;padding:14px 26px;border-radius:999px;border:1px solid var(--accent);transition:transform .15s,box-shadow .15s}}
.btn:hover{{transform:translateY(-1px);box-shadow:0 8px 22px -10px var(--accent)}}
.btn.ghost{{background:transparent;color:var(--ink);border-color:var(--line)}}
.top .btn{{padding:10px 20px;font-size:.92rem}}
.hero{{padding:64px 0 72px}}.hero .wrap{{display:grid;grid-template-columns:1.02fr 1fr;gap:56px;align-items:center}}
.eyebrow{{font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:18px}}
.lead{{font-size:1.12rem;color:var(--muted);max-width:34em}}
.cta{{display:flex;flex-wrap:wrap;gap:12px;margin:30px 0 0}}
.himg{{position:relative}}
.ph{{position:relative;overflow:hidden;border-radius:var(--r);background:linear-gradient(135deg,var(--soft),var(--line));aspect-ratio:4/3}}
.ph span{{position:absolute;inset:0;display:grid;place-items:center;color:var(--muted);font-size:.85rem;letter-spacing:.08em;text-transform:uppercase}}
.ph img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.ph.hero-ph{{aspect-ratio:4/5;max-height:620px;width:100%}}.ph.tall{{aspect-ratio:4/5}}
.ill{{position:absolute;right:14px;bottom:14px;background:rgba(0,0,0,.45);color:#fff;font-size:.7rem;padding:4px 9px;border-radius:99px;letter-spacing:.04em}}
.hcard{{position:absolute;left:-28px;bottom:36px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 20px;box-shadow:0 18px 40px -22px rgba(0,0,0,.35);display:flex;flex-direction:column;max-width:250px}}
.hcard strong{{font-family:var(--disp);font-size:1.35rem;line-height:1.2}}.hcard span{{font-size:.85rem;color:var(--muted)}}
.trust{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--surface)}}
.trust ul{{list-style:none;margin:0 auto;padding:26px 24px;max-width:1180px;display:grid;grid-template-columns:repeat(4,1fr);gap:24px}}
.trust li{{display:flex;flex-direction:column}}.trust strong{{font-family:var(--disp);font-size:1.2rem}}.trust span{{font-size:.88rem;color:var(--muted)}}
.sec{{padding:96px 0}}.band-soft{{background:var(--soft)}}
.head{{max-width:640px;margin-bottom:48px}}
.svc-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.svc{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:30px 28px;transition:border-color .2s}}
.svc:hover{{border-color:var(--accent)}}
.svc .num{{display:block;font-size:.8rem;color:var(--accent);font-weight:600;letter-spacing:.1em;margin-bottom:14px}}
.svc p{{color:var(--muted);font-size:.97rem;margin:0}}.svc .price{{margin-top:14px;color:var(--ink);font-weight:600}}
.svc-note{{margin-top:26px;color:var(--muted);font-size:.95rem}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}}
.checks{{list-style:none;padding:0;margin:24px 0 0;display:grid;gap:12px}}
.checks li{{padding-left:30px;position:relative}}.checks li::before{{content:"";position:absolute;left:0;top:.55em;width:16px;height:9px;border-left:2px solid var(--accent);border-bottom:2px solid var(--accent);transform:rotate(-45deg) translateY(-4px)}}
.gal{{padding-top:0}}.gal-grid{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:16px}}.gal-grid .ph{{aspect-ratio:auto;height:340px}}
.note{{font-size:.82rem;color:var(--muted);margin-top:12px}}
.steps{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,1fr);gap:40px}}
.steps span{{display:block;font-family:var(--disp);font-size:3rem;line-height:1;color:var(--accent);margin-bottom:16px}}
.steps p{{color:var(--muted);margin:0}}
.rev{{display:grid;grid-template-columns:auto 1fr;gap:56px;align-items:center;border:1px solid var(--line);border-radius:var(--r);padding:40px 48px;background:var(--surface)}}
.score{{display:flex;flex-direction:column;align-items:flex-start}}.score .big{{font-family:var(--disp);font-size:3.6rem;line-height:1}}
.stars{{color:var(--accent);letter-spacing:3px;margin:6px 0}}.score span{{font-size:.9rem;color:var(--muted)}}
.quote{{font-family:var(--disp);font-size:1.5rem;line-height:1.35;margin:0}}
.faq{{max-width:820px}}details{{border-bottom:1px solid var(--line);padding:20px 0}}
summary{{cursor:pointer;font-weight:600;font-size:1.06rem;list-style:none;display:flex;justify-content:space-between;gap:20px}}
summary::after{{content:"+";color:var(--accent);font-size:1.4rem;line-height:1}}details[open] summary::after{{content:"–"}}
details p{{color:var(--muted);margin:12px 0 0}}
.contact{{display:grid;grid-template-columns:1fr 1.15fr;gap:24px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:36px}}
.card p{{margin:0 0 14px;display:flex;flex-direction:column}}.lbl{{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
.card a{{text-decoration:none}}.card .phone{{font-family:var(--disp);font-size:1.7rem}}
.hours{{border-collapse:collapse;width:100%;font-size:.95rem}}.hours th{{text-align:left;font-weight:500;padding:6px 0;color:var(--muted)}}.hours td{{text-align:right;padding:6px 0}}
.hours tr+tr{{border-top:1px solid var(--line)}}
.tag{{display:inline-block!important;font-size:.75rem;background:var(--soft);color:var(--muted);padding:3px 10px;border-radius:99px;margin-top:8px!important}}
.map{{border-radius:var(--r);overflow:hidden;border:1px solid var(--line);min-height:420px;background:var(--soft)}}.map iframe{{width:100%;height:100%;min-height:420px;border:0;display:block}}
.ctaband{{background:var(--dark);color:#fff;padding:72px 0}}.ctaband .wrap{{display:flex;justify-content:space-between;align-items:center;gap:32px;flex-wrap:wrap}}
.ctaband h2{{margin:0;max-width:18em}}.ctaband .btn{{background:#fff;color:var(--dark);border-color:#fff}}
footer{{background:var(--dark);color:rgba(255,255,255,.65);font-size:.88rem;border-top:1px solid rgba(255,255,255,.12);padding:28px 0 96px}}
footer .wrap{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
.mbar{{display:none}}
@media (max-width:900px){{
 .nav{{display:none}}.hero{{padding:32px 0 48px}}.hero .wrap,.split,.contact{{grid-template-columns:1fr;gap:32px}}
 .ph.hero-ph{{aspect-ratio:4/3}}.hcard{{left:12px;bottom:12px}}
 .trust ul{{grid-template-columns:1fr 1fr}}.svc-grid,.steps{{grid-template-columns:1fr}}
 .gal-grid{{grid-template-columns:1fr 1fr}}.gal-grid .ph:first-child{{grid-column:1/-1}}.gal-grid .ph{{height:220px}}
 .sec{{padding:64px 0}}.rev{{grid-template-columns:1fr;gap:20px;padding:28px}}
 .top .btn{{display:none}}
 .mbar{{display:grid;grid-template-columns:1fr 1fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:30;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:var(--surface);border-top:1px solid var(--line)}}
 .mbar a{{text-align:center;padding:13px;border-radius:999px;text-decoration:none;font-weight:600;font-size:.95rem}}
 .mbar .m1{{background:var(--accent);color:var(--accent-ink)}}.mbar .m2{{border:1px solid var(--line)}}
}}
</style>
</head>
<body>
<div class="nb">Nezávazný návrh webu – není to oficiální stránka firmy {E(name)}</div>
<div class="top" role="banner"><div class="wrap">
  <a class="logo" href="#"><b>{E(f["logo"])}</b><small>{E(f["logo_sub"])}</small></a>
  <nav class="nav" aria-label="Hlavní menu">{nav}</nav>
  <a class="btn" href="{tel}">{E(phone)}</a>
</div></div>
<main>
<section class="hero"><div class="wrap">
  <div>
    <p class="eyebrow">{E(f["eyebrow"])}</p>
    <h1>{E(f["h1"])}</h1>
    <p class="lead">{E(f["lead"])}</p>
    <div class="cta"><a class="btn" href="{tel}">{E(f["cta"])}</a><a class="btn ghost" href="#{f["cta2"][0]}">{E(f["cta2"][1])}</a></div>
  </div>
  <div class="himg">{img(f["hero_photo"], 1400, f["hero_alt"], "hero-ph", True)}<span class="ill">Ilustrační foto</span>{hero_card}</div>
</div></section>
<div class="trust"><ul>{trust}</ul></div>
<section class="sec" id="sluzby"><div class="wrap">
  <div class="head"><p class="eyebrow">{E(f["svc_eyebrow"])}</p><h2>{E(f["svc_title"])}</h2><p class="lead">{E(f["svc_lead"])}</p></div>
  <div class="svc-grid">{services}</div>
  <p class="svc-note">{E(f["svc_note"])}</p>
</div></section>
{gallery}
<section class="sec band-soft" id="o-nas"><div class="wrap split">
  {img(f["about"]["photo"], 1200, f["about"]["alt"], "tall")}
  <div><p class="eyebrow">{E(f["about"]["eyebrow"])}</p><h2>{E(f["about"]["title"])}</h2>
  <p class="lead">{E(f["about"]["text"])}</p><ul class="checks">{about_list}</ul></div>
</div></section>
{review}
<section class="sec" id="postup"><div class="wrap">
  <div class="head"><p class="eyebrow">Jak to probíhá</p><h2>{E(f["steps_title"])}</h2></div>
  <ol class="steps">{steps}</ol>
</div></section>
{extra}
<section class="sec" id="otazky"><div class="wrap faq">
  <div class="head"><p class="eyebrow">Časté otázky</p><h2>Na co se nás lidé ptají</h2></div>{faq}
</div></section>
<section class="sec band-soft" id="kontakt"><div class="wrap">
  <div class="head"><p class="eyebrow">Kontakt</p><h2>{E(f["contact_title"])}</h2></div>
  <div class="contact">
    <div class="card">
      <p><span class="lbl">Telefon</span><a class="phone" href="{tel}">{E(phone)}</a></p>
      {email_html}
      <p><span class="lbl">Adresa</span>{E(addr)}<a href="{maps}" style="color:var(--accent);font-size:.92rem;margin-top:4px">Navigovat →</a></p>
      {addr_note}
      {ico}
      {hours}
    </div>
    <div class="map"><iframe title="Mapa – {E(name)}" loading="lazy" src="{embed}"></iframe></div>
  </div>
</div></section>
<section class="ctaband"><div class="wrap"><h2>{E(f["band"])}</h2><a class="btn" href="{tel}">Zavolat {E(phone)}</a></div></section>
</main>
<footer><div class="wrap"><span>© 2026 {E(name)} · {E(addr)}</span><span>Návrh webu připravil Lukáš Trnka · studio.webycz@gmail.com</span></div></footer>
<div class="mbar"><a class="m1" href="{tel}">Zavolat</a>{sms}</div>
<script>
// Stín záhlaví po posunutí stránky
(function(){{var t=document.querySelector('.top');addEventListener('scroll',function(){{t.style.boxShadow=scrollY>8?'0 6px 24px -18px rgba(0,0,0,.4)':'none'}},{{passive:true}})}})();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    root = pathlib.Path(sys.argv[2])
    only = set(sys.argv[3:])
    for f in data:
        if only and f["slug"] not in only:
            continue
        d = root / f["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(build(f), encoding="utf-8")
        print("ok", f["slug"])

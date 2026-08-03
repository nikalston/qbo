# Quality Order — PWA

Beer order sheet for the Quality Beverage book, Table & Vine / Big Y Franklin.
Standalone: does not share storage, SKUs, or code with the inventory app.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app — UI, logic, and the SKU list are all in here |
| `manifest.webmanifest` | Makes it installable to the home screen |
| `sw.js` | Service worker; caches everything so it runs with no signal |
| `icon-*.png` | Home screen icons |
| `items.csv` | The SKU list — **this is the file you edit** |
| `build_pwa.py` | Pushes `items.csv` into `index.html` and bumps the cache |
| `icons.py` | Regenerates the icons if you want a different mark |

## Hosting

Needs HTTPS or localhost — service workers won't register over plain HTTP,
so a bare `file://` open will run but won't install or cache.

**Cloudflare Pages:** drag the folder into a new project. Done.

**Hostinger VPS:** drop the folder under your web root, make sure the cert
covers it, load it in Safari.

**Local test on the desktop:**
```
cd qbo && python3 -m http.server 8000
```
then open `http://localhost:8000`.

## Installing on the iPhone

Safari → open the URL → Share → **Add to Home Screen**. It has to be Safari;
Chrome on iOS can't install PWAs. Launch it from the home screen icon, not
from a Safari tab — that's what gives you the standalone window with no
address bar, and it's a separate storage bucket from the browser.

## Using it

- **+ / −** step by one case. Tap the number itself to type a quantity
  straight in — faster than twelve taps on Mich Ultra.
- The header keeps a running **cases / lines** count. Each section header
  shows its own subtotal in amber once anything's on it.
- **Ordered only** filters to just the lines you've touched — that's your
  review pass on the way back up the aisle.
- **Review order** shows the finished order as plain text in your format
  (`4 - BUD LIGHT 2/12 CAN 12oz`), grouped by section, with a case/line
  total at the bottom. **Copy** or **Share** from there.
- **Clear** wipes all quantities. It asks first.

Quantities save on every tap, so backgrounding the app or getting pulled
away mid-aisle won't lose the count.

## Changing the SKU list

Edit `items.csv` (`section,item` — order in the file is the order in the app),
then:

```
python3 build_pwa.py items.csv
```

Re-upload. The build stamps a new cache name, so phones pick up the new list
on next launch instead of serving the old one forever. If a phone looks stale,
force-quit the app and reopen — the new worker activates on the next start.

The same `items.csv` drives the printed Scribe sheet via `make_order_sheet.py`,
so one edit keeps both in sync.

## Worth knowing

- iOS can evict PWA storage after long stretches of non-use. You're opening
  this weekly, so it shouldn't bite — but export the order when you finish it
  rather than leaving it parked in the app for days.
- There's no undo beyond stepping the number back down.
- No sync, no account, no server. The order lives on that one phone until you
  copy it out.

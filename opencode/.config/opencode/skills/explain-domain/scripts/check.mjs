#!/usr/bin/env node
// Browser check for the exact file you will deliver: node check.mjs PAGE.html [--out DIR]
// Exercises every stepper, chart readout and TOC link; checks overflow, console errors, network, label collisions and no-JS reading.
// Exit 0 = pass, 1 = failures listed, 2 = no browser available (report which checks did not run).
import { createHash } from 'node:crypto';
import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { homedir } from 'node:os';

const args = process.argv.slice(2);
const file = resolve(args[0] ?? '');
const out = resolve(args.includes('--out') ? args[args.indexOf('--out') + 1] : dirname(file));
if (!args[0] || !existsSync(file)) { console.error('usage: node check.mjs PAGE.html [--out DIR]'); process.exit(2); }

function loadPlaywright() {
  const roots = [process.env.PLAYWRIGHT_CORE_DIR, process.cwd(), join(homedir(), '.agents/skills/visual-explainer'), join(homedir(), '.claude/skills/visual-explainer')];
  try { roots.push(execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim()); } catch {}
  for (const root of roots.filter(Boolean)) {
    for (const name of ['playwright-core', 'playwright']) {
      try { return createRequire(join(root, 'noop.js'))(name); } catch {}
      try { return createRequire(join(root, 'node_modules', 'noop.js'))(name); } catch {}
    }
  }
  return null;
}
const pw = loadPlaywright();
if (!pw) { console.log('SKIP no playwright-core found; set PLAYWRIGHT_CORE_DIR or run static checks and say browser behaviour was not exercised.'); process.exit(2); }
async function launch() {
  try { return await pw.chromium.launch(); } catch {}
  for (const p of ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']) {
    if (existsSync(p)) try { return await pw.chromium.launch({ executablePath: p }); } catch {}
  }
  return null;
}
const browser = await launch();
if (!browser) { console.log('SKIP no Chromium or Chrome could launch.'); process.exit(2); }

mkdirSync(out, { recursive: true });
const url = pathToFileURL(file).href;
const hash = createHash('sha256').update(readFileSync(file)).digest('hex');
const fails = [], passes = [];
const ok = (cond, pass, fail) => (cond ? passes : fails).push(cond ? pass : fail);

// Text that collides with other text, with a node box it doesn't belong to, or leaves the drawing.
const collisions = () => [...document.querySelectorAll('svg.ve-svg')].flatMap((svg, si) => {
  const vis = el => { for (let n = el; n && n !== svg; n = n.parentNode) { const cs = getComputedStyle(n); if (cs.display === 'none' || +cs.opacity === 0 || cs.visibility === 'hidden') return false; } return true; };
  const texts = [...svg.querySelectorAll('text')].filter(t => !t.closest('.hov') && t.textContent.trim() && vis(t)).map(t => ({ t, r: t.getBoundingClientRect() }));
  const boxes = [...svg.querySelectorAll('.nd-box')].map(b => ({ b, r: b.getBoundingClientRect() }));
  const s = svg.getBoundingClientRect(), hit = (a, b, pad = 1) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > pad && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > pad;
  const name = t => JSON.stringify(t.textContent.trim().slice(0, 40));
  const issues = [];
  texts.forEach((a, i) => texts.slice(i + 1).forEach(b => { if (hit(a.r, b.r, 2)) issues.push(`figure ${si + 1}: text ${name(a.t)} overlaps ${name(b.t)}`); }));
  texts.forEach(a => boxes.forEach(b => { if (a.t.parentNode !== b.b.parentNode && hit(a.r, b.r, 2)) issues.push(`figure ${si + 1}: text ${name(a.t)} overlaps a node box`); }));
  texts.forEach(a => { if (a.r.left < s.left - 1 || a.r.right > s.right + 1 || a.r.top < s.top - 1 || a.r.bottom > s.bottom + 1) issues.push(`figure ${si + 1}: text ${name(a.t)} is clipped by the drawing edge`); });
  return issues;
});

try {
  const page = await browser.newPage({ offline: true, viewport: { width: 1440, height: 900 } });
  const errors = [], requests = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('request', r => requests.push(r.url()));
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(400);
  await page.screenshot({ path: join(out, 'check-first-screen.png') });

  const walks = page.locator('[data-walk]');
  for (let i = 0; i < await walks.count(); i++) {
    const w = walks.nth(i), name = `stepper ${i + 1}`;
    ok(await w.evaluate(el => el.classList.contains('live')), `${name} enhanced`, `${name} not enhanced by kit.js`);
    const n = await w.locator('.walk-caps > li').count(), rail = await w.locator('[data-to]').count();
    ok(n > 1 && n === rail, `${name}: ${n} steps`, `${name}: ${n} captions vs ${rail} rail buttons`);
    await w.locator('[data-to="1"]').click();
    const seen = new Set();
    for (let k = 0; k < n; k++) {
      seen.add(await w.locator('.walk-cap').innerText());
      if (k < n - 1) await w.locator('[data-step]').click();
    }
    ok(seen.size === n, `${name}: Next reaches ${n} distinct captions`, `${name}: only ${seen.size}/${n} distinct captions`);
    ok(await w.locator('[data-step]').innerText() === 'Restart', `${name}: last step offers Restart`, `${name}: last step label is not Restart`);
    await w.locator('[data-back]').click();
    ok((await w.locator('[aria-current="step"]').getAttribute('data-to')) === String(n - 1), `${name}: Back works`, `${name}: Back did not move to step ${n - 1}`);
    await w.locator(`[data-to="${n}"]`).focus(); await page.keyboard.press('Enter');
    ok((await w.locator('[aria-current="step"]').getAttribute('data-to')) === String(n), `${name}: rail works by keyboard`, `${name}: rail Enter did not select the step`);
    await page.waitForTimeout(1300);
    const hidden = await w.locator('[data-w]').evaluateAll(ps => ps.filter(p => getComputedStyle(p).opacity === '0').length);
    ok(hidden === 0, `${name}: every part visible at the last step`, `${name}: ${hidden} parts still hidden at the last step`);
  }
  await page.waitForTimeout(1300);

  const charts = page.locator('svg[data-hover]');
  for (let i = 0; i < await charts.count(); i++) {
    const c = charts.nth(i), name = `chart ${i + 1}`;
    await c.evaluate(s => { for (let d = s.closest('details'); d; d = d.parentElement.closest('details')) d.open = true; });
    await c.scrollIntoViewIfNeeded();
    const head = () => c.locator('.tip .tb').first().textContent();
    const rest = await head();
    await c.focus(); await page.keyboard.press('Home'); const a = await head();
    await page.keyboard.press('ArrowRight'); const b = await head();
    await page.keyboard.press('End'); const z = await head();
    const live = await c.evaluate(s => s.parentNode.querySelector(':scope > .vh[aria-live]')?.textContent || '');
    ok(a !== b && b !== z && live.length > 0, `${name}: Home/Right/End move the readout and announce it`, `${name}: keyboard readout did not move (${a} → ${b} → ${z}) or was not announced`);
    const box = await c.boundingBox();
    await page.mouse.move(box.x + box.width * .3, box.y + box.height / 2); const p1 = await head();
    await page.mouse.move(box.x + box.width * .7, box.y + box.height / 2); const p2 = await head();
    ok(p1 !== p2, `${name}: pointer moves the readout`, `${name}: pointer did not move the readout`);
    await page.mouse.move(0, 0);
    ok(await head() === rest, `${name}: readout rests on "${rest}"`, `${name}: readout did not return to its resting point`);
    const tipIn = await c.evaluate(s => { const t = s.querySelector('.tip').getBoundingClientRect(), r = s.getBoundingClientRect(); return t.left >= r.left - 2 && t.right <= r.right + 2; });
    ok(tipIn, `${name}: tooltip stays inside the chart`, `${name}: tooltip leaves the chart`);
  }

  const links = await page.locator('a[href^="#"]').evaluateAll(as => as.filter(a => !document.getElementById(decodeURIComponent(a.hash.slice(1)))).map(a => a.hash));
  ok(links.length === 0, 'all in-page links resolve', `broken in-page links: ${links.join(', ')}`);
  const col = await page.evaluate(collisions);
  ok(col.length === 0, 'no SVG label collisions or clipping (all steps shown)', col.slice(0, 12).join('\n  '));
  ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'no page overflow at 1440px', 'page overflows horizontally at 1440px');
  const outbound = await page.locator('a[href^="http"]').count();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: join(out, 'check-desktop.png'), fullPage: true });

  await page.setViewportSize({ width: 320, height: 800 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.reload(); await page.waitForTimeout(300);
  ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'no page overflow at 320px (wide figures scroll inside their frame)', 'page overflows horizontally at 320px');
  const motion = await page.evaluate(() => [...document.querySelectorAll('.wdraw,.draw,.nd-box')].some(e => parseFloat(getComputedStyle(e).transitionDuration) > 0));
  ok(!motion, 'reduced motion removes transitions', 'transitions still run under reduced motion');
  await page.screenshot({ path: join(out, 'check-320.png'), fullPage: true });
  ok(errors.length === 0, 'no console errors', `console errors: ${errors.join(' | ')}`);
  const remote = requests.filter(r => r !== url && !r.startsWith('data:'));
  ok(remote.length === 0, 'no network requests beyond the file itself', `unexpected requests: ${remote.slice(0, 5).join(', ')}`);

  const plain = await browser.newPage({ offline: true, javaScriptEnabled: false, viewport: { width: 1440, height: 900 } });
  await plain.goto(url);
  const caps = await plain.locator('.walk-caps').evaluateAll(l => l.every(e => getComputedStyle(e).display !== 'none'));
  const hiddenParts = await plain.locator('[data-w]').evaluateAll(ps => ps.filter(p => getComputedStyle(p).opacity === '0').length);
  ok(caps && hiddenParts === 0, 'without JavaScript every figure part and step caption is readable', 'without JavaScript some figure parts or captions are hidden');
  if (outbound) passes.push(`${outbound} outbound link(s): confirm each is approved for the audience`);
} finally { await browser.close(); }

for (const p of passes) console.log('PASS ' + p);
for (const f of fails) console.log('FAIL ' + f);
console.log(`${fails.length ? 'FAILED' : 'PASSED'} ${file}\nsha256 ${hash}\nscreenshots ${join(out, 'check-first-screen.png')}, check-desktop.png, check-320.png`);
process.exit(fails.length ? 1 : 0);

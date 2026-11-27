// explain-domain kit. Inlined by `scripts/figures.py inline`. Each block enhances markup that already reads well without it.
const SVG = 'http://www.w3.org/2000/svg';
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Entrance motion: [data-reveal] figures draw, fade, grow or pop once when they scroll into view.
(() => {
  if (reduced || !('IntersectionObserver' in window)) return;
  const els = [...document.querySelectorAll('[data-reveal]')];
  document.documentElement.classList.add('rv');
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('seen'); io.unobserve(e.target); }
  }), { threshold: .15 });
  els.forEach(e => io.observe(e));
  addEventListener('beforeprint', () => els.forEach(e => e.classList.add('seen')));
})();

// Stepper: parts with data-w="n" appear at step n; the rail, Back/Next and caption stay in sync.
document.querySelectorAll('[data-walk]').forEach(f => {
  const caps = [...f.querySelectorAll('.walk-caps > li')].map(l => l.innerHTML);
  const max = caps.length, cap = f.querySelector('.walk-cap');
  const next = f.querySelector('[data-step]'), back = f.querySelector('[data-back]');
  const tabs = [...f.querySelectorAll('[data-to]')], parts = [...f.querySelectorAll('[data-w]')];
  let k = 1;
  const set = n => {
    k = Math.max(1, Math.min(max, n));
    parts.forEach(p => { const w = +p.dataset.w; p.classList.toggle('on', w <= k); p.classList.toggle('now', w === k); });
    tabs.forEach(t => {
      const w = +t.dataset.to;
      t.classList.toggle('done', w < k);
      w === k ? t.setAttribute('aria-current', 'step') : t.removeAttribute('aria-current');
    });
    cap.innerHTML = '<span class="walk-k">' + k + ' / ' + max + '</span>' + caps[k - 1];
    next.textContent = k === max ? 'Restart' : 'Next';
    back.disabled = k === 1;
  };
  f.classList.add('live');
  next.addEventListener('click', () => set(k === max ? 1 : k + 1));
  back.addEventListener('click', () => set(k - 1));
  tabs.forEach(t => t.addEventListener('click', () => set(+t.dataset.to)));
  addEventListener('beforeprint', () => set(max));
  set(+f.dataset.start || 1);
});

// On-page navigation: draws the rail and moves a thumb over the headings in view.
(() => {
  const nav = document.querySelector('.toc');
  if (!nav || !('IntersectionObserver' in window)) return;
  const links = [...nav.querySelectorAll('a')], rails = [...nav.querySelectorAll('.rail path')];
  const thumb = nav.querySelector('.thumb'), box = thumb && thumb.parentNode;
  const targets = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1))));
  if (targets.includes(null)) return console.warn('toc: a link has no target');
  const heads = targets.map(t => t.matches('section') ? t.querySelector('h2') || t : t.matches('details') ? t.querySelector('summary') : t);
  const dx = a => a.classList.contains('d2') ? 14 : 0;
  const seg = i => {
    const a = links[i], p = links[i - 1], n = links[i + 1];
    return [a.offsetTop + (p && dx(p) !== dx(a) ? 7 : 0), a.offsetTop + a.offsetHeight - (n && dx(n) !== dx(a) ? 7 : 0)];
  };
  const seen = new Set(); let cur = 0;
  // Headings in view are all active; with none in view, the last heading above the middle of the view is.
  const above = () => { let n = 0; heads.forEach((h, i) => { const r = h.getBoundingClientRect(); if (r.height && r.top < innerHeight / 2) n = i; }); return n; };
  const update = () => {
    const on = links.map((_, i) => seen.size ? seen.has(i) : i === cur);
    links.forEach((a, i) => on[i] ? a.setAttribute('data-active', '') : a.removeAttribute('data-active'));
    if (thumb && box.offsetHeight) thumb.style.clipPath = 'inset(' + (seg(on.indexOf(true))[0] - 1) + 'px 0 ' + (box.offsetHeight - seg(on.lastIndexOf(true))[1] - 1) + 'px 0)';
  };
  const draw = () => {
    const d = links.map((a, i) => { const [t, b] = seg(i); return (i ? 'L' : 'M') + (dx(a) + 1) + ' ' + t + 'V' + b; }).join('');
    rails.forEach(r => r.setAttribute('d', d)); update();
  };
  const io = new IntersectionObserver(es => {
    es.forEach(e => { const i = heads.indexOf(e.target); e.intersectionRatio >= .9 ? seen.add(i) : seen.delete(i); });
    if (!seen.size) cur = above(); else if (!seen.has(cur)) cur = Math.min(...seen);
    update();
  }, { threshold: .9 });
  heads.forEach(h => io.observe(h));
  links.forEach((a, i) => a.addEventListener('click', () => { const d = targets[i].closest('details'); if (d) d.open = true; cur = i; update(); }));
  addEventListener('resize', draw); if (document.fonts) document.fonts.ready.then(draw);
  cur = above(); draw();
})();

// Crosshair readout: svg[data-hover] holds {names:[[name, unit class, "hollow"?]], rows:[[label, x, [[y|null, text], ...]]], at, top, bottom}.
// It rests on row `at` (the point the page is about), follows the pointer, and moves with Left/Right, Home/End; Shift moves 10.
document.querySelectorAll('svg[data-hover]').forEach(s => {
  const spec = JSON.parse(s.dataset.hover), rows = spec.rows, vb = s.viewBox.baseVal;
  const el = (tag, attrs, parent) => { const n = document.createElementNS(SVG, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); parent.appendChild(n); return n; };
  const g = el('g', { class: 'hov', 'aria-hidden': 'true' }, s);
  const vl = el('line', { y1: spec.top, y2: spec.bottom }, g);
  const dots = spec.names.map(([, unit, style]) => el('circle', { r: 5, class: [unit, style].filter(Boolean).join(' ') }, g));
  const tip = el('g', { class: 'tip' }, g), rect = el('rect', { rx: 6, height: 30 + 22 * spec.names.length }, tip);
  const head = el('text', { class: 'tb', x: 12, y: 24 }, tip);
  const vals = spec.names.map(([name], j) => {
    const t = el('text', { class: 'td', x: 12, y: 46 + 22 * j }, tip);
    t.textContent = name + ' ';
    return el('tspan', { class: 'tb' }, t);
  });
  const say = s.parentNode.appendChild(Object.assign(document.createElement('p'), { className: 'vh' }));
  say.setAttribute('aria-live', 'polite');
  const rest = spec.at ?? 0;
  let k = rest;
  const show = (i, speak) => {
    k = Math.max(0, Math.min(rows.length - 1, i));
    const [label, x, v] = rows[k];
    vl.setAttribute('x1', x); vl.setAttribute('x2', x); head.textContent = label;
    v.forEach(([y, text], j) => {
      dots[j].style.display = y === null ? 'none' : '';
      if (y !== null) { dots[j].setAttribute('cx', x); dots[j].setAttribute('cy', y); }
      vals[j].textContent = text;
    });
    const w = Math.ceil(Math.max(head.getComputedTextLength(), ...vals.map(t => t.parentNode.getComputedTextLength())) + 24);
    rect.setAttribute('width', w);
    const ty = spec.ty ?? spec.top;
    tip.setAttribute('transform', 'translate(' + (x + 14 + w > vb.x + vb.width - 4 ? x - 14 - w : x + 14) + ',' + ty + ')');
    if (speak) say.textContent = label + ': ' + v.map(([, t], j) => spec.names[j][0] + ' ' + t).join(', ');
  };
  s.addEventListener('pointermove', e => {
    const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(s.getScreenCTM().inverse());
    let best = 0;
    rows.forEach((r, i) => { if (Math.abs(r[1] - p.x) < Math.abs(rows[best][1] - p.x)) best = i; });
    if (best !== k) show(best);
  });
  s.addEventListener('pointerleave', () => show(rest));
  // Text can't be measured while hidden, so re-measure when an enclosing <details> opens.
  s.closest('details')?.addEventListener('toggle', () => show(k));
  s.addEventListener('keydown', e => {
    const j = e.shiftKey ? 10 : 1;
    const m = { ArrowLeft: k - j, ArrowRight: k + j, Home: 0, End: rows.length - 1 }[e.key];
    if (m === undefined) return;
    e.preventDefault(); show(m, true);
  });
  show(rest);
});

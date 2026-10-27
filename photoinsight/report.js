'use strict';
const $ = id => document.getElementById(id);
const number = (v, digits = 0) => v == null ? '—' : Number(v).toLocaleString('pl-PL', { maximumFractionDigits: digits });
const percent = v => v == null ? '—' : `${number(v * 100, 1)}%`;
const share = (n, d) => d ? n / d : null;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const labels = { camera: 'Aparat', lens: 'Obiektyw', focalLength: 'Ogniskowa rzeczywista', focalLength35: 'Ekwiwalent 35 mm', aperture: 'Przysłona', iso: 'ISO', exposure: 'Czas ekspozycji', takenAt: 'Data', year: 'Rok', month: 'Miesiąc', hour: 'Godzina' };
const months = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień'];
const charts = window.reportCharts = new Map();
let report;
const dataset = () => report[$('dataset').value];
const distribution = (s, field) => s.distributions.find(d => d.field === field).groups;
const coverage = (s, field) => s.coverage.find(d => d.field === (['year', 'month', 'hour', 'cameraYear'].includes(field) ? 'takenAt' : field));
const unit = s => s.unit === 'files' ? 'plików' : 'ujęć';
const format = (field, v) => {
  if (field === 'camera' || field === 'lens') return v;
  if (field === 'year') return String(v);
  if (field === 'month') return months[Number(v) - 1];
  if (field === 'hour') return `${String(v).padStart(2, '0')}:00`;
  if (field === 'aperture') return `f/${number(v, 2)}`;
  if (field === 'exposure') return Number(v) >= 1 ? `${number(v, 4)} s` : `1/${number(1 / Number(v), 1)} s`;
  return `${number(v, field === 'focalLength35' ? 4 : 2)}${['focalLength', 'focalLength35'].includes(field) ? ' mm' : ''}`;
};
const sorted = (groups, field) => [...groups].sort((a, b) => ['camera', 'lens'].includes(field) ? b.count - a.count || a.value.localeCompare(b.value, 'pl') : Number(a.value) - Number(b.value));
function note(s, field) {
  const c = coverage(s, field);
  return `${s.unit === 'files' ? 'Portfolio · pliki' : 'Archiwum · potwierdzone ujęcia'}. Znane: ${number(c.known)} / ${number(s.count)} ${unit(s)}; braki: ${number(c.missing)}. Udziały wśród ${number(c.known)} znanych wartości.`;
}
function metric(label, value, detail) { return `<article class="metric"><div class="metric-label">${esc(label)}</div><div class="metric-value">${esc(value)}</div><small>${esc(detail)}</small></article>`; }
function rows(id, groups, field, known) {
  $(id).innerHTML = groups.map(g => `<tr><td>${esc(format(field, g.value))}</td><td>${number(g.count)}</td><td>${percent(share(g.count, known))}</td></tr>`).join('');
}
function chart(id, option) {
  let c = charts.get(id);
  if (!c) { c = echarts.init($(id), null, { renderer: 'svg' }); charts.set(id, c); }
  c.setOption({ animation: !matchMedia('(prefers-reduced-motion: reduce)').matches, animationDuration: 250, color: ['#527f4d', '#adc78d', '#719f99', '#d9b374', '#9cae98', '#bba1ad'], textStyle: { fontFamily: 'Segoe UI, sans-serif', fontSize: 11, color: '#60705a' }, aria: { enabled: true }, tooltip: { trigger: 'axis', renderMode: 'richText', confine: true, backgroundColor: '#fff', textStyle: { color: '#31442e', fontSize: 11 } }, ...option }, true);
}
function bars(id, groups, field, known, horizontal = false) {
  const values = sorted(groups, field);
  const zoom = !horizontal && values.length > 16;
  chart(id, {
    grid: { left: horizontal ? (innerWidth < 500 ? 118 : 250) : 48, right: 26, top: 14, bottom: zoom ? 92 : 60 },
    xAxis: horizontal ? { type: 'value', minInterval: 1 } : { type: 'category', data: values.map(g => format(field, g.value)), axisLabel: { rotate: values.length > 8 ? 40 : 0, hideOverlap: true } },
    yAxis: horizontal ? { type: 'category', inverse: true, data: values.map(g => format(field, g.value)), axisLabel: { width: innerWidth < 500 ? 105 : 235, overflow: 'truncate', fontSize: 10 }, axisTick: { show: false } } : { type: 'value', minInterval: 1, splitLine: { lineStyle: { type: 'dashed', color: '#e9eee3' } } },
    dataZoom: zoom ? [{ type: 'slider', start: 0, end: 100, bottom: 8, height: 20, brushSelect: false }, { type: 'inside', zoomOnMouseWheel: false }] : [],
    tooltip: { trigger: 'axis', renderMode: 'richText', confine: true, formatter: p => { const g = values[p[0].dataIndex]; return `${format(field, g.value)}\n${number(g.count)} / ${number(known)} znanych (${percent(share(g.count, known))})`; } },
    series: [{ name: 'Liczba', type: 'bar', barMaxWidth: 28, data: values.map(g => g.count), itemStyle: { color: '#a9c67f', borderRadius: horizontal ? [0, 3, 3, 0] : [3, 3, 0, 0] } }]
  });
  return values;
}
function renderOverview() {
  const p = report.portfolio, focal = [...distribution(p, 'focalLength')].sort((a, b) => b.count - a.count)[0];
  const aperture = [...distribution(p, 'aperture')].sort((a, b) => b.count - a.count)[0];
  const camera = coverage(p, 'camera');
  $('metrics').innerHTML = metric('Pliki portfolio', number(p.count), 'Pliki, bez scalania wersji w ujęcia') + metric('Rozpoznane aparaty', number(distribution(p, 'camera').length), `${number(camera.known)} / ${number(p.count)} plików; braki: ${number(camera.missing)}`) + metric('Najczęstsza ogniskowa', focal ? `${number(focal.value, 1)} mm` : '—', `${number(focal?.count)} / ${number(coverage(p, 'focalLength').known)} znanych; braki: ${number(coverage(p, 'focalLength').missing)}`) + metric('Najczęstsza przysłona', aperture ? format('aperture', aperture.value) : '—', `${number(aperture?.count)} / ${number(coverage(p, 'aperture').known)} znanych; braki: ${number(coverage(p, 'aperture').missing)}`);
  $('portfolio-range').textContent = `Daty zdjęć: ${p.dateRange.first ?? '—'} → ${p.dateRange.last ?? '—'}`;
  $('hero-title').textContent = focal ? `${number(focal.value, 1)} mm. Ogniskowa, do której wracasz.` : 'Każdy wybór zostawia ślad.';
  $('hero-value').textContent = focal ? number(focal.value, 1) : '—';
  $('hero-description').textContent = focal ? `${percent(share(focal.count, coverage(p, 'focalLength').known))} plików ze znaną ogniskową zapisano przy ${number(focal.value, 1)} mm (${number(focal.count)} / ${number(coverage(p, 'focalLength').known)}). Braki ogniskowej: ${number(coverage(p, 'focalLength').missing)} / ${number(p.count)}. To opis wyborów w portfolio, a nie całej aktywności fotograficznej.` : 'Brak danych o ogniskowej w zapisanym zbiorze.';
  $('coverage-rows').innerHTML = p.coverage.map(c => `<tr><td>${esc(labels[c.field])}</td><td>${number(c.known)}</td><td>${number(c.missing)}</td><td>${percent(share(c.known, p.count))}</td></tr>`).join('');
}
function renderEquipment() {
  const s = dataset(), field = $('equipment-field').value;
  $('equipment-note').textContent = note(s, field);
  const values = bars('equipment-chart', distribution(s, field), field, coverage(s, field).known, true);
  rows('equipment-rows', values, field, coverage(s, field).known);
}
function renderParameters() {
  const s = dataset(), field = $('parameter-field').value;
  $('parameter-note').textContent = note(s, field);
  $('parameter-warning').textContent = field === 'focalLength35' ? 'Ekwiwalent 35 mm jest osobnym parametrem; nie zastępuje ogniskowej rzeczywistej. Zachowano precyzję eksportu do czterech miejsc po przecinku. Suwak przybliża fragment rozkładu.' : 'Wykres pokazuje wszystkie zapisane wartości; przy długiej osi użyj suwaka. Powiększenie nie zmienia mianownika.';
  const values = bars('parameter-chart', distribution(s, field), field, coverage(s, field).known);
  rows('parameter-rows', values, field, coverage(s, field).known);
}
function renderTime() {
  const s = dataset(), field = $('time-field').value;
  $('time-note').textContent = note(s, field) + (field === 'cameraYear' ? ' Przekrój aparat × rok pochodzi z zapisanego agregatu. Aparat bez rozpoznanego modelu pozostaje osobną kategorią.' : '');
  if (field !== 'cameraYear') {
    $('time-head').innerHTML = '<tr><th>Okres</th><th>Liczba</th><th>Udział datowanych</th></tr>';
    rows('time-rows', bars('time-chart', distribution(s, field), field, coverage(s, field).known), field, coverage(s, field).known);
    return;
  }
  const years = [...new Set(s.cameraYear.map(g => g.year))].sort(), cameras = [...new Set(s.cameraYear.map(g => g.camera))];
  chart('time-chart', { legend: { bottom: 0, type: 'scroll', textStyle: { fontSize: 10 } }, grid: { left: 48, right: 20, top: 20, bottom: 85 }, xAxis: { type: 'category', data: years }, yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#e9eee3', type: 'dashed' } } }, series: cameras.map(camera => ({ name: camera ?? 'Brak aparatu', type: 'bar', stack: 'year', barMaxWidth: 75, data: years.map(year => s.cameraYear.filter(g => g.year === year && g.camera === camera).reduce((sum, g) => sum + g.count, 0)) })) });
  $('time-head').innerHTML = '<tr><th>Rok / aparat</th><th>Liczba</th><th>Udział datowanych</th></tr>';
  $('time-rows').innerHTML = s.cameraYear.map(g => `<tr><td>${g.year} / ${esc(g.camera ?? 'Brak aparatu')}</td><td>${number(g.count)}</td><td>${percent(share(g.count, coverage(s, 'year').known))}</td></tr>`).join('');
}
function renderComparison() {
  const field = $('compare-field').value, session = $('compare-weight').value === 'session';
  const d = report.comparison.distributions.find(d => d.field === field);
  const groups = [...d.groups].sort((a, b) => ['camera', 'lens'].includes(field) ? (b.portfolioShare ?? 0) - (a.portfolioShare ?? 0) : Number(a.value) - Number(b.value));
  const ps = g => g[session ? 'portfolioSessionShare' : 'portfolioShare'];
  const as = g => g[session ? 'archiveSessionShare' : 'archiveShare'];
  $('comparison-note').textContent = `Potwierdzone ujęcia. Portfolio: ${number(d.portfolioKnown)} / ${number(report.comparison.portfolioCount)} znanych; braki: ${number(d.portfolioMissing)}. Archiwum: ${number(d.archiveKnown)} / ${number(report.comparison.archiveCount)} znanych; braki: ${number(d.archiveMissing)}. Oś pokazuje udziały (%).`;
  $('weight-note').textContent = session ? 'Każda sesja ze znanym parametrem ma równą wagę, osobno w każdym zbiorze. Udział ważony nie jest ilorazem liczników ujęć w tabeli. Sesja to przybliżenie na podstawie folderu.' : 'Każde potwierdzone ujęcie ma równą wagę. Udział to liczba ujęć z daną wartością podzielona przez liczbę znanych wartości tego parametru w danym zbiorze.';
  const horizontal = ['camera', 'lens'].includes(field), zoom = groups.length > (horizontal ? 12 : 14);
  chart('comparison-chart', {
    legend: { bottom: 0, data: ['Portfolio', 'Archiwum'] },
    grid: { left: horizontal ? (innerWidth < 500 ? 118 : 250) : 48, right: 20, top: 20, bottom: zoom ? 115 : 90 },
    xAxis: horizontal ? { type: 'value', axisLabel: { formatter: '{value}%' } } : { type: 'category', data: groups.map(g => format(field, g.value)), axisLabel: { rotate: groups.length > 8 ? 40 : 0, hideOverlap: true } },
    yAxis: horizontal ? { type: 'category', inverse: true, data: groups.map(g => format(field, g.value)), axisLabel: { width: innerWidth < 500 ? 105 : 235, overflow: 'truncate', fontSize: 10 } } : { type: 'value', axisLabel: { formatter: '{value}%' } },
    dataZoom: zoom ? [{ type: 'slider', xAxisIndex: horizontal ? undefined : 0, yAxisIndex: horizontal ? 0 : undefined, start: 0, end: 100, bottom: 40, height: 18, brushSelect: false }] : [],
    tooltip: { trigger: 'axis', renderMode: 'richText', confine: true, formatter: p => { const g = groups[p[0].dataIndex]; return `${format(field, g.value)}\nPortfolio: ${percent(ps(g))} · ${number(g.portfolioCount)} / ${number(d.portfolioKnown)} ujęć\nArchiwum: ${percent(as(g))} · ${number(g.archiveCount)} / ${number(d.archiveKnown)} ujęć${session ? '\nUdziały z równymi wagami sesji' : ''}`; } },
    series: [{ name: 'Portfolio', type: 'bar', barMaxWidth: 22, data: groups.map(g => ps(g) == null ? null : ps(g) * 100) }, { name: 'Archiwum', type: 'bar', barMaxWidth: 22, data: groups.map(g => as(g) == null ? null : as(g) * 100) }]
  });
  $('comparison-rows').innerHTML = groups.map(g => `<tr><td>${esc(format(field, g.value))}</td><td>${number(g.portfolioCount)} / ${number(d.portfolioKnown)}</td><td>${number(g.archiveCount)} / ${number(d.archiveKnown)}</td><td>${percent(ps(g))}</td><td>${percent(as(g))}</td><td>${ps(g) == null || as(g) == null ? '—' : number((ps(g) - as(g)) * 100, 1)}</td><td>${as(g) > 0 && ps(g) != null ? `${number(ps(g) / as(g), 2)}×` : '—'}</td></tr>`).join('');
}
function renderComparisonSummary() {
  const c = report.comparison;
  $('comparison-metrics').innerHTML = metric('Portfolio w porównaniu', number(c.portfolioCount), 'Potwierdzone ujęcia · wersje liczone raz') + metric('Zachowane archiwum', number(c.archiveCount), 'Potwierdzone ujęcia z importu') + metric('Ujęcia wspólne', number(c.overlap), `${number(c.portfolioOnly)} dodatkowe ujęcia tylko w portfolio`);
  $('comparison-scope').textContent = `Do porównania weszło ${number(c.confirmedPortfolioFiles)} z ${number(c.portfolioFiles)} plików portfolio, scalonych do ${number(c.portfolioCount)} potwierdzonych ujęć. Pominięto ${number(c.excludedPortfolioFiles)} plików portfolio bez potwierdzonego dopasowania. W całym imporcie poza potwierdzonymi wynikami pozostają ${number(c.unresolvedImages)} nieprzypisane pliki obrazów i ${number(c.provisionalCaptures)} prowizoryczne ujęcia; te kategorie mogą się pokrywać. Porównanie obejmuje inny zakres niż przegląd ${number(report.portfolio.count)} plików i inne daty zbiorów.`;
}
function observation(index, title, body, evidence) { return `<article class="observation"><span class="index">${String(index).padStart(2, '0')}</span><h3>${esc(title)}</h3><p>${esc(body)}</p><p class="evidence">${esc(evidence)}</p></article>`; }
function renderObservations() {
  const p = report.portfolio;
  const defs = [
    ['camera', 'Aparat najczęściej obecny w portfolio', null],
    ['lens', 'Obiektyw najczęściej obecny w portfolio', null],
    ['year', 'Najliczniejszy rok w portfolio', null],
    ['focalLength', 'Dłuższa perspektywa', v => Number(v) >= 70],
    ['aperture', 'Otwarta przysłona', v => Number(v) <= 2.8],
    ['iso', 'ISO od 1600', v => Number(v) >= 1600]
  ];
  $('observations').innerHTML = defs.map(([field, title, test], i) => {
    const groups = distribution(p, field), c = coverage(p, field), top = [...groups].sort((a, b) => b.count - a.count)[0];
    const count = test ? groups.filter(g => test(g.value)).reduce((n, g) => n + g.count, 0) : top?.count ?? 0;
    const body = test ? `${field === 'focalLength' ? 'Rzeczywista ogniskowa od 70 mm' : field === 'aperture' ? 'Przysłona f/2,8 lub jaśniejsza' : 'ISO co najmniej 1600'}: ${percent(share(count, c.known))} plików ze znaną wartością.` : `${top ? format(field, top.value) : 'Brak danych'}: ${percent(share(count, c.known))} plików ze znaną wartością.`;
    return observation(i + 1, title, body, `Portfolio · pliki: ${number(count)} / ${number(c.known)} znanych. Braki: ${number(c.missing)} / ${number(p.count)}.`);
  }).join('');
  $('features').innerHTML = report.comparison.features.slice(0, 6).map((f, i) => {
    const d = report.comparison.distributions.find(d => d.field === f.field), g = f.data;
    return observation(i + 1, f.title, `Portfolio ${percent(g.portfolioShare)}; archiwum ${percent(g.archiveShare)}. Różnica: ${number(g.deltaPoints, 1)} p.p. Po wyrównaniu aparat × rok: ${percent(f.adjustedPortfolioShare)} vs ${percent(f.adjustedArchiveShare)}.`, `Ujęcia: portfolio ${number(g.portfolioCount)} / ${number(d.portfolioKnown)} (braki ${number(d.portfolioMissing)}); archiwum ${number(g.archiveCount)} / ${number(d.archiveKnown)} (braki ${number(d.archiveMissing)}). Korekta: ${number(f.adjustedPortfolioKnown)} wspieranych ujęć portfolio; wykluczone: ${number(f.unsupportedPortfolio)}.`);
  }).join('');
}
function renderDates() {
  const date = v => v == null ? 'Nieznana' : new Date(v).toLocaleString('pl-PL', { timeZone: 'Europe/Warsaw', dateStyle: 'long', timeStyle: 'short' }) + ' · Europe/Warsaw';
  const p = report.portfolio, a = report.archive;
  $('snapshot-dates').innerHTML = [['Snapshot portfolio', date(p.snapshotAt)], ['Snapshot importu archiwum', date(a.snapshotAt)], ['Wygenerowanie raportu', date(report.generatedAt)], ['Zakres dat portfolio', `${p.dateRange.first ?? '—'} → ${p.dateRange.last ?? '—'} · braki dat: ${number(coverage(p, 'year').missing)} / ${number(p.count)} plików`], ['Zakres dat archiwum', `${a.dateRange.first ?? '—'} → ${a.dateRange.last ?? '—'} · braki dat: ${number(coverage(a, 'year').missing)} / ${number(a.count)} ujęć`]].map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
}
async function init() {
  try {
    const response = await fetch('./report.json');
    if (!response.ok) throw new Error('Błąd odczytu raportu');
    report = await response.json();
    if (report.schemaVersion !== 1) throw new Error('Nieobsługiwana wersja raportu');
    window.photoReport = report;
    $('content').hidden = false;
    renderOverview(); renderEquipment(); renderParameters(); renderTime(); renderComparisonSummary(); renderComparison(); renderObservations(); renderDates();
    $('dataset').addEventListener('change', () => { renderEquipment(); renderParameters(); renderTime(); });
    $('equipment-field').addEventListener('change', renderEquipment);
    $('parameter-field').addEventListener('change', renderParameters);
    $('time-field').addEventListener('change', renderTime);
    for (const id of ['compare-field', 'compare-weight']) $(id).addEventListener('change', renderComparison);
    let resizeTimer;
    addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { for (const c of charts.values()) c.resize(); renderEquipment(); renderComparison(); }, 120); });
    const observer = new IntersectionObserver(entries => { for (const e of entries) if (e.isIntersecting) { for (const a of document.querySelectorAll('nav a')) { const active = a.hash === `#${e.target.id}`; a.classList.toggle('active', active); if (active) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); } } }, { rootMargin: '-10% 0px -65% 0px' });
    for (const s of document.querySelectorAll('section')) observer.observe(s);
    document.body.dataset.ready = 'true';
  } catch (e) { $('content').hidden = true; $('error').hidden = false; console.error(e); }
  finally { $('loading').hidden = true; }
}
init();

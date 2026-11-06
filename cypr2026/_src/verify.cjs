/* Browser regressions for the accepted audit. Runs locally, never publishes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {chromium} = require('playwright');
const {default:AxeBuilder} = require('@axe-core/playwright');
const startServer = require('./local_server.cjs');
const root = path.resolve(__dirname, '..');
const output = process.env.CYPR_TEST_OUTPUT || fs.mkdtempSync(path.join(os.tmpdir(), 'cypr2026-tests-'));

(async () => {
  const overrides = new Map();
  // Serve from the repository root to exercise the real /cypr2026/ SW scope.
  const {server, url:origin} = await startServer(path.dirname(root), overrides);
  const url = origin + path.basename(root) + '/';
  const browser = await chromium.launch({headless:true,...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {channel:'chrome'})});
  const results = [];
  let failures = 0;
  async function test(name, fn) {
    if (process.env.CYPR_TEST_FILTER && !name.includes(process.env.CYPR_TEST_FILTER)) return;
    try { await fn(); results.push({name,pass:true}); console.log('PASS',name); }
    catch (error) { failures++; results.push({name,pass:false,error:error.stack}); console.error('FAIL',name,error.message); }
  }
  const errors = [];
  const watch = page => page.on('pageerror', error => errors.push(error.message));
  try {
    for (const timezoneId of ['UTC','Europe/Warsaw','Asia/Nicosia','America/Los_Angeles']) {
      await test('Today transitions and resume · ' + timezoneId, async () => {
        const context = await browser.newContext({timezoneId,serviceWorkers:'block',viewport:{width:1440,height:1000}});
        try {
          const page = await context.newPage(); watch(page);
          await page.clock.install({time:new Date('2026-11-09T11:29:00Z')});
          await page.goto(url,{waitUntil:'networkidle'});
          assert.match(await page.locator('.today-point h4').innerText(),/Aphrodite/);
          const checkbox = page.locator('[data-check-id]').first();
          await checkbox.check({force:true});
          await page.locator('[data-today-actions] a').first().focus();
          await page.evaluate(() => {window.focusedBefore = document.activeElement; window.disclosureBefore = Array.from(document.querySelectorAll('details')).map(e=>e.open);});
          await page.clock.runFor(21*60*1000);
          assert.match(await page.locator('.today-point h4').innerText(),/Polis/);
          assert.match(await page.locator('.today-next').innerText(),/15:00/);
          assert(await page.evaluate(() => window.focusedBefore === document.activeElement));
          assert(await checkbox.isChecked());
          assert(await page.evaluate(() => JSON.stringify(window.disclosureBefore) === JSON.stringify(Array.from(document.querySelectorAll('details')).map(e=>e.open))));
          await page.clock.setSystemTime(new Date('2026-11-09T14:30:00Z'));
          await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
          assert.match(await page.locator('.today-point h4').innerText(),/Edro/);
          await page.clock.setSystemTime(new Date('2026-11-09T15:10:00Z'));
          await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true})));
          assert.match(await page.locator('.today-point h4').innerText(),/Powrót/);
          await page.clock.setSystemTime(new Date('2026-11-09T22:01:00Z'));
          await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
          assert.match(await page.locator('[data-today-title]').innerText(),/Artemis/);
          assert(await checkbox.isChecked());
          assert(await page.evaluate(() => JSON.stringify(window.disclosureBefore) === JSON.stringify(Array.from(document.querySelectorAll('details')).map(e=>e.open))));
          await page.reload({waitUntil:'networkidle'});
          assert(await checkbox.isChecked());
        } finally { await context.close(); }
      });
    }
    await test('Responsive layouts and text 200% · 360 / 390 / 768 / 1440', async () => {
      const context = await browser.newContext({serviceWorkers:'block'});
      try {
        const page = await context.newPage(); watch(page);
        for (const width of [360,390,768,1440]) {
          await page.setViewportSize({width,height:900});
          await page.goto(url+'?date=2026-11-09',{waitUntil:'networkidle'});
          for (const size of [16,32]) {
            await page.evaluate(size=>{document.documentElement.style.fontSize=size+'px';},size);
            const menu=page.locator('.subnav__more');
            if(await menu.isVisible()) await menu.evaluate(el=>el.open=true);
            const state = await page.evaluate(() => ({viewport:innerWidth,document:document.documentElement.scrollWidth,
              clipped:Array.from(document.querySelectorAll('#dzis p,#dzis h3,#dzis h4,#dzis dd,.hero__edition')).filter(e=>e.clientWidth>0 && e.scrollWidth>e.clientWidth+2).map(e=>e.className)}));
            assert(state.document<=state.viewport+1,JSON.stringify({width,size,...state}));
            assert.equal(state.clipped.length,0,JSON.stringify({width,size,...state}));
            if(await menu.isVisible()) await menu.evaluate(el=>el.open=false);
            await page.locator('#dzis').scrollIntoViewIfNeeded();
            await page.screenshot({path:path.join(output,`today-${width}-${size}.png`)});
          }
        }
      } finally { await context.close(); }
    });
    await test('Map coverage, navigation, gallery and keyboard', async () => {
      const context = await browser.newContext({serviceWorkers:'block',viewport:{width:1440,height:1000}});
      try {
        const page = await context.newPage(); watch(page);
        await page.goto(url,{waitUntil:'networkidle'});
        for (const day of ['02','03','04','05','06']) {
          await page.locator(`.map-filter__chip[data-map-day="${day}"]`).click();
          await page.waitForFunction(()=>document.querySelector('.leaflet-marker-icon') && !document.querySelector('[data-map-status]').textContent.includes(': 0 z'));
          const status = await page.locator('[data-map-status]').innerText();
          const matches=status.match(/(\d+) z (\d+) miejsc/);
          assert(matches && matches[1]===matches[2],status);
        }
        const plan=JSON.parse(fs.readFileSync(path.join(root,'data/Cypr_2026_zrodlo_prawdy.json'),'utf8'));
        assert(plan.places.find(p=>p.id==='POI-ARTEMIS').map_url.includes('34.933166,32.871986'));
        assert(plan.places.find(p=>p.id==='POI-PARK').map_kind.includes('wejście'));
        assert.equal(await page.locator('.day-brief').count(),7);
        await page.locator('[data-gallery-filter="place"]').click();
        const trigger=page.locator('#photo-gallery [data-lightbox="place-neophytos"]').first();
        await trigger.click();
        await page.waitForFunction(()=>{let i=document.querySelector('#photo-lightbox-img');return i.complete&&i.naturalWidth>1;});
        await page.keyboard.press('ArrowRight');
        assert(await page.locator('#photo-lightbox').evaluate(el=>el.open));
        await page.keyboard.press('Escape');
        assert(await trigger.evaluate(el=>el===document.activeElement));
      } finally { await context.close(); }
    });
    await test('Route coordinates, app links, issues and return placeholders', async () => {
      const context=await browser.newContext({serviceWorkers:'block',viewport:{width:390,height:900}});
      try {
        const page=await context.newPage();watch(page);
        await page.goto(url+'?date=2026-11-09',{waitUntil:'networkidle'});
        assert.equal(await page.locator('[data-issues-disclosure]').evaluate(el=>el.open),false);
        await page.locator('[data-issues-disclosure]').evaluate(el=>el.open=true);
        assert.match(await page.locator('[data-issue-due-label]').first().innerText(),/zaległe/);
        const route=page.locator('#trasa-aphrodite');
        const plan=JSON.parse(fs.readFileSync(path.join(root,'data/Cypr_2026_zrodlo_prawdy.json'),'utf8'));
        const start=plan.places.find(p=>p.id==='POI-BATHS').coordinates;
        assert((await route.innerText()).includes(String(start.lat)));
        for(const href of ['https://maps.apple.com/','om://map','geo:']) {
          const link=route.locator(`a[href^="${href}"]`);
          assert.equal(await link.count(),1);
          assert.equal(await link.getAttribute('data-requires-network'),null);
        }
        const google=route.locator('a[href^="https://www.google.com/maps/"]');
        assert.equal(await google.getAttribute('data-requires-network'),'true');
        await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
        await route.locator('[data-copy-coordinates]').click();
        assert((await page.evaluate(()=>getSelection().toString())).includes(String(start.lat)));
        assert.match(await page.locator('#bezpieczenstwo').innerText(),/Paphos General Hospital[\s\S]*WPISZ/);
        assert.match(await page.locator('#auto').innerText(),/WPISZ: sektor, klucze/);
        const day4=page.locator('#day-04');
        assert.match(await day4.textContent(),/07:00[\s\S]*09:30[\s\S]*13:45/);
      } finally {await context.close();}
    });
    await test('No JavaScript and print state restoration', async () => {
      const context = await browser.newContext({javaScriptEnabled:false,serviceWorkers:'block'});
      try {
        const page=await context.newPage();await page.goto(url,{waitUntil:'networkidle'});
        assert.equal(await page.locator('[data-day-disclosure][open]').count(),7);
        assert.match(await page.locator('#auto .car-facts').innerText(),/10:30[\s\S]*03:30/);
        assert(await page.locator('#auto .car-facts').isVisible());
        assert.equal(await page.locator('.day-brief').count(),7);
        await page.emulateMedia({media:'print'});
        assert(await page.locator('#day-07 .timeline').isVisible());
      } finally {await context.close();}
      const c=await browser.newContext({serviceWorkers:'block',viewport:{width:390,height:900}});
      try {
        const page=await c.newPage();await page.goto(url,{waitUntil:'networkidle'});
        const before=await page.locator('details').evaluateAll(els=>els.map(el=>el.open));
        await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
        assert(await page.locator('details').evaluateAll(els=>els.every(el=>el.open)));
        await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
        assert.deepEqual(await page.locator('details').evaluateAll(els=>els.map(el=>el.open)),before);
      } finally {await c.close();}
    });
    await test('Accessibility · axe WCAG 2.2 AA · 390 / 1440', async () => {
      const context=await browser.newContext({serviceWorkers:'block'});
      try {
        const page=await context.newPage();
        for(const width of [390,1440]) {
          await page.setViewportSize({width,height:1000});await page.goto(url,{waitUntil:'networkidle'});
          const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
          assert.equal(result.violations.length,0,JSON.stringify(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
        }
      } finally {await context.close();}
    });
    await test('Failed initial offline install cannot claim readiness; retry completes', async () => {
      const context=await browser.newContext();
      const failing='/'+path.basename(root)+'/cypr2026-handbook.pdf';
      try {
        overrides.set(failing,{status:503});
        const page=await context.newPage();await page.goto(url,{waitUntil:'networkidle'});
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.includes('Nie udało się'),null,{timeout:60000});
        assert(await page.locator('[data-offline-photos]').isHidden());
        overrides.delete(failing);await page.locator('[data-offline-retry]').click();
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'),null,{timeout:60000});
      } finally {overrides.delete(failing);await context.close();}
    });
    await test('Fresh offline save, unopened photos, repair and SW update', async () => {
      const context=await browser.newContext({viewport:{width:390,height:900}});
      try {
        const page=await context.newPage();watch(page);
        await page.goto(url,{waitUntil:'networkidle'});
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'),null,{timeout:60000});
        const key=await page.locator('[data-check-id]').first().getAttribute('data-check-id');
        await page.locator('[data-check-id]').first().check({force:true});
        // An image absent from precache must not be claimed as ready after deletion.
        const small=await page.evaluate(async()=>{
          const photo=JSON.parse(document.querySelector('#photo-lightbox-data').textContent).find(p=>p.slot==='place-neophytos');
          const keys=await caches.keys();const name=keys.find(k=>k.startsWith('cypr-2026-'));const cache=await caches.open(name);
          await cache.delete(new URL(photo.fallback,location.href));return photo.fallback;
        });
        await page.evaluate(()=>window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true})));
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.includes('nie jest potwierdzony'));
        await page.locator('[data-offline-retry]').click();
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'),null,{timeout:60000});
        assert(await page.evaluate(async small=>!!await caches.match(small),small));
        await context.setOffline(true);
        await page.reload({waitUntil:'networkidle'});
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'));
        assert(await page.locator(`[data-check-id="${key}"]`).isChecked());
        assert(await page.locator('#dzis [data-today-body]').isVisible());
        assert(await page.locator('#dzis [data-today-body]').innerText());
        await page.locator('#day-03 [data-day-disclosure]').evaluate(el=>el.open=true);
        assert(await page.locator('#day-03 .timeline').isVisible());
        await page.locator('#mapa').scrollIntoViewIfNeeded();
        await page.waitForSelector('.leaflet-marker-icon');
        assert.match(await page.locator('header.hero [data-connection]').innerText(),/Offline — plan z pamięci/);
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Offline layout overflow');
        const plan=JSON.parse(fs.readFileSync(path.join(root,'data/Cypr_2026_zrodlo_prawdy.json'),'utf8'));
        const tracks=plan.routes.filter(r=>r.gpx.path);
        if(tracks.length) {
          // A country overview can quantize a small trail to a flat SVG path.
          // Exercise the actual control that fits a route before asserting paint.
          await page.locator(`[data-map-route="${tracks[0].id}"]`).click();
          await page.waitForSelector('[data-gpx-route]');
          for(const route of tracks) {
            const response=await page.evaluate(async file=>{const r=await fetch(file);return {status:r.status,type:r.headers.get('Content-Type')};},route.gpx.path);
            assert.equal(response.status,200);assert.match(response.type,/application\/gpx\+xml/);
          }
        }
        for(const slot of ['place-neophytos','place-choirokoitia-d','place-choirokoitia-e','place-pissouri-d','day-07-b','route-vouni-d']) {
          await page.locator(`[data-gallery-filter="all"]`).click();
          await page.locator(`#photo-gallery [data-lightbox="${slot}"]`).click();
          await page.waitForFunction(slot=>{let i=document.querySelector('#photo-lightbox-img');return i.complete&&i.naturalWidth>1&&i.currentSrc.includes('/'+slot+'/');},slot);
          assert(await page.locator('#photo-lightbox-img').evaluate(async img=>!!await caches.match(img.currentSrc)));
          await page.keyboard.press('Escape');
        }
        for(const file of ['cypr2026-handbook.pdf','cal/cypr2026-caly-wyjazd.ics']) assert(await page.evaluate(async file=>(await fetch(file)).ok,file));
        assert.equal(await page.evaluate(async()=>!!await caches.match('cypr2026-print.pdf')),false);
        await context.setOffline(false);
        await page.locator('[data-offline-pdf]').click();
        await page.waitForFunction(()=>document.querySelector('[data-offline-pdf-status]').textContent==='Pełny PDF zapisany offline.');
        await context.setOffline(true);
        assert(await page.evaluate(async()=>{const r=await fetch('cypr2026-print.pdf');return r.ok&&r.headers.get('Content-Type').includes('application/pdf');}));
        await context.setOffline(false);
        await page.locator('[data-offline-photos]').click();
        await page.waitForFunction(()=>document.querySelector('[data-offline-photos-status]').textContent.startsWith('Duże zdjęcia zapisane offline'),null,{timeout:60000});
        await context.setOffline(true);
        await page.locator('#photo-gallery [data-lightbox="place-neophytos"]').click();
        await page.waitForFunction(()=>{const i=document.querySelector('#photo-lightbox-img');return i.complete&&i.naturalWidth>800;});
        await page.keyboard.press('Escape');await context.setOffline(false);
        const old=fs.readFileSync(path.join(root,'sw.js'),'utf8');
        const name=old.match(/const CACHE_VERSION = "([^"]+)"/)[1];
        overrides.set('/'+path.basename(root)+'/sw.js',{body:old.replace(name,name+'-verification')});
        await page.evaluate(async()=>{const registration=await navigator.serviceWorker.getRegistration();await registration.update();});
        await page.waitForFunction(async()=> (await caches.keys()).some(k=>k.endsWith('-verification')),null,{timeout:60000});
        await page.waitForFunction(async()=>!(await caches.keys()).some(k=>k.startsWith('cypr-2026-')&&!k.endsWith('-verification')),null,{timeout:60000});
        // The modified test SW differs from the document, so readiness must be withdrawn.
        await page.locator('[data-offline-retry]').click();
        await page.waitForFunction(()=>!document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'));
        assert(await page.locator(`[data-check-id="${key}"]`).isChecked());
        await context.setOffline(true);await page.reload({waitUntil:'networkidle'});
        assert.equal(await page.locator('.day-brief').count(),7);
      } finally {overrides.clear();await context.close();}
    });
    await test('Synthetic GPX offline rendering and MIME repair (in-memory fixture only)', async () => {
      const context=await browser.newContext({viewport:{width:390,height:900}});
      try {
        const fixturePath='/'+path.basename(root)+'/gpx/synthetic-test.gpx';
        const plan=JSON.parse(fs.readFileSync(path.join(root,'data/Cypr_2026_zrodlo_prawdy.json'),'utf8'));
        plan.routes[0].gpx.path='gpx/synthetic-test.gpx';
        plan.routes[0].name='Synthetic test only';
        const html=fs.readFileSync(path.join(root,'index.html'),'utf8').replace(/(<script type="application\/json" id="cypr-data">).*?(<\/script>)/s,(_,a,b)=>a+JSON.stringify(plan).replace(/<\//g,'<\\/')+b);
        overrides.set('/'+path.basename(root)+'/',{type:'text/html',body:html});
        overrides.set('/'+path.basename(root)+'/index.html',{type:'text/html',body:html});
        overrides.set(fixturePath,{type:'application/octet-stream',body:'<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg><trkpt lat="35.056063" lon="32.345565"/><trkpt lat="35.086063" lon="32.395565"/></trkseg></trk></gpx>'});
        const worker=fs.readFileSync(path.join(root,'sw.js'),'utf8').replace('const PRECACHE_URLS = [','const PRECACHE_URLS = ["./gpx/synthetic-test.gpx",');
        overrides.set('/'+path.basename(root)+'/sw.js',{body:worker});
        const page=await context.newPage();watch(page);
        await page.goto(url,{waitUntil:'networkidle'});
        await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'),null,{timeout:60000});
        await context.setOffline(true);
        await page.reload({waitUntil:'networkidle'});
        await page.locator('#mapa').scrollIntoViewIfNeeded();
        await page.waitForSelector('[data-gpx-route="TR-APHRODITE"]');
        const response=await page.evaluate(async()=>{const r=await fetch('gpx/synthetic-test.gpx');return {status:r.status,type:r.headers.get('Content-Type'),body:await r.text()};});
        assert.equal(response.status,200);assert.equal(response.type,'application/gpx+xml');assert.match(response.body,/<trkseg>/);
        assert(await page.locator('[data-map-offline]').first().isVisible());
      } finally {overrides.clear();await context.close();}
    });
    assert.equal(errors.length,0,'Page errors: '+errors.join('; '));
  } finally {
    fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({results,errors},null,2));
    await browser.close();await new Promise(resolve=>server.close(resolve));
    console.log('Artifacts:',output);
  }
  if(failures)process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});

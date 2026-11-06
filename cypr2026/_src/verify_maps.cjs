/* Real data, geometry, downloads and browser rendering. Never publishes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const startServer = require('./local_server.cjs');
const root = path.resolve(__dirname, '..');
const output = process.env.CYPR_MAP_OUTPUT || fs.mkdtempSync(path.join(os.tmpdir(), 'cypr2026-maps-'));
fs.mkdirSync(output, {recursive:true});
const plan = JSON.parse(fs.readFileSync(path.join(root, 'data/Cypr_2026_zrodlo_prawdy.json'), 'utf8'));
const tracks = plan.routes.filter(r=>r.gpx.path);
const sha = bytes=>crypto.createHash('sha256').update(bytes).digest('hex');

(async()=>{
 const overrides = new Map();
 const packed = process.env.CYPR_SITE_MODE==='dist';
 const subpath = packed ? '' : path.basename(root)+'/';
 const {server,url:origin} = await startServer(packed ? path.join(root,'dist') : path.dirname(root),overrides);
 const url = origin + subpath;
 const browser = await chromium.launch({headless:true,...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {channel:'chrome'})});
 const evidence={version:plan.meta.version,layout:packed?'Cloudflare root / dist':'GitHub /cypr2026/',checkedAt:new Date().toISOString(),widths:[],errors:[],failures:[]};
 async function instrument(context){
  await context.addInitScript(()=>{
   window.__maps=[];
   document.addEventListener('load',event=>{
    if(event.target.tagName==='SCRIPT' && /\/leaflet\.js(?:\?|$)/.test(event.target.src)){
     window.L.Map.addInitHook(function(){window.__maps.push(this);});
    }
   },true);
  });
 }
 async function mainReady(page){
  await page.locator('#map-canvas').scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>window.__maps?.some(m=>m.getContainer().id==='map-canvas'));
  await page.waitForFunction(n=>document.querySelector('[data-map-routes-status]').textContent.split('przebieg wczytany').length-1===n,tracks.length);
 }
 async function snapshot(page){return page.evaluate(()=>{
  const map=window.__maps.find(m=>m.getContainer().id==='map-canvas');
  const ids=new Set(),routes=[];
  map.eachLayer(l=>{
   const popup=l.getPopup?.();
   if(popup)for(const match of popup.getContent().matchAll(/href="#place-(POI-[A-Z0-9-]+)"/g))ids.add(match[1]);
   const route=l.getElement?.()?.getAttribute('data-gpx-route');
   if(route)routes.push({id:route,points:l.getLatLngs().length,d:l.getElement().getAttribute('d')});
  });
  return {ids:[...ids].sort(),routes,cards:[...document.querySelectorAll('[data-place-id]')].filter(e=>!e.hidden).map(e=>e.dataset.placeId).sort(),
   optional:[...document.querySelectorAll('.place-card--optional')].filter(e=>!e.hidden).map(e=>e.dataset.placeId).sort(),status:document.querySelector('[data-map-status]').textContent,
   overflow:document.documentElement.scrollWidth>innerWidth+1};
 });}
 async function capture(page,name){await page.locator('.map-frame').screenshot({path:path.join(output,name+'.png')});}
 try {
  for(const width of [390,1440]){
   const context=await browser.newContext({viewport:{width,height:950},serviceWorkers:'block',reducedMotion:'reduce',acceptDownloads:true});
   await instrument(context);const page=await context.newPage();page.on('pageerror',e=>evidence.errors.push(e.message));
   const record={width,days:[],routes:[],cycling:[]};evidence.widths.push(record);
   try {
    await page.goto(url,{waitUntil:'networkidle'});await mainReady(page);
    record.all=await snapshot(page);assert.equal(record.all.ids.length,50);assert.equal(record.all.cards.length,50);assert.equal(record.all.routes.length,7);assert(!record.all.overflow);
    await capture(page,`mapa-${width}-wszystkie`);
    await page.locator('[data-map-extent="all"]').click();
    assert(await page.evaluate(()=>{const m=window.__maps.find(m=>m.getContainer().id==='map-canvas');return m.getBounds().contains([52.4462125,20.6513339]);}));
    assert.equal((await snapshot(page)).ids.length,50);await capture(page,`mapa-${width}-takze-lotniska`);
    await page.locator('[data-map-extent="cyprus"]').click();
    for(const day of plan.days){
     const dayNo=day.id.slice(-2);
     const base=new Set(day.timeline.filter(e=>!e.optional).flatMap(e=>e.place_ids));
     const primary=plan.routes.find(r=>r.id===day.primary_route_id);if(primary)base.add(primary.start_place_id);
     const ids=new Set([...base,...day.timeline.flatMap(e=>e.place_ids),...day.optional_stops.map(s=>s.place_id)]);
     await page.locator(`[data-map-day="${dayNo}"].map-filter__chip`).click();
     await page.waitForTimeout(100);
     const state=await snapshot(page);assert.deepEqual(state.ids,[...ids].sort());assert.deepEqual(state.cards,[...ids].sort());
     assert.deepEqual(state.optional,[...ids].filter(id=>!base.has(id)).sort());
     assert.deepEqual(state.routes.map(r=>r.id).sort(),tracks.filter(r=>ids.has(r.start_place_id)).map(r=>r.id).sort());
     assert.match(state.status,new RegExp(`${ids.size} z ${ids.size} miejsc`));assert(!state.overflow);
     record.days.push({day:day.id,...state});await capture(page,`mapa-${width}-${day.id}`);
    }
    // Keyboard activation of a day chip, then real route controls and downloads.
    const chip=page.locator('[data-map-day="02"].map-filter__chip');await chip.focus();await page.keyboard.press('Space');assert.equal(await chip.getAttribute('aria-pressed'),'true');
    await page.locator('details.route-details').evaluateAll(items=>items.forEach(e=>e.open=true));
    for(const route of tracks){
     const button=page.locator(`[data-map-route="${route.id}"]`);await button.focus();await page.keyboard.press('Enter');
     await page.waitForFunction(id=>document.querySelectorAll(`[data-gpx-route="${id}"]`).length===1,route.id);
     await page.waitForTimeout(120);const state=await snapshot(page);assert.deepEqual(state.routes.map(r=>r.id),[route.id]);
     assert(state.routes[0].d && state.routes[0].d!=='M0 0','Missing painted SVG path: '+route.id);
     const [download]=await Promise.all([page.waitForEvent('download'),page.locator(`a[download][href="${route.gpx.path}"]`).click()]);
     const dest=path.join(output,`${width}-${download.suggestedFilename()}`);await download.saveAs(dest);
     assert.equal(sha(fs.readFileSync(dest)),route.gpx.sha256);
     const response=await page.evaluate(async file=>{const r=await fetch(file);const xml=new DOMParser().parseFromString(await r.text(),'application/xml');return {status:r.status,type:r.headers.get('content-type'),points:xml.getElementsByTagNameNS('*','trkpt').length};},route.gpx.path);
     assert.equal(response.status,200);assert.match(response.type,/application\/gpx\+xml/);assert.equal(response.points,state.routes[0].points);
     record.routes.push({id:route.id,download:download.suggestedFilename(),...response,painted:true});await capture(page,`trasa-${width}-${route.id}`);
    }
    await page.locator('[data-map-day="all"].map-filter__chip').click();
    const marker=page.locator('#map-canvas .leaflet-marker-icon').first();await marker.focus();await page.keyboard.press('Enter');await page.waitForSelector('.leaflet-popup-content');await page.keyboard.press('Escape');
    for(const bike of plan.cycling_options.options.filter(b=>b.map.status==='preview')){
     const canvas=page.locator(`[data-cycling-map="${bike.id}"]`);await canvas.scrollIntoViewIfNeeded();await page.waitForFunction(id=>document.querySelector(`[data-cycling-map="${id}"]`).dataset.mapReady==='true',bike.id);
     const geo=await page.evaluate(id=>{const m=window.__maps.find(m=>m.getContainer().dataset.cyclingMap===id);let pts=[];m.eachLayer(l=>{if(l instanceof L.Polyline)pts=l.getLatLngs().map(p=>[p.lat,p.lng]);});return pts;},bike.id);
     assert.deepEqual(geo,bike.map.points);record.cycling.push({id:bike.id,points:geo.length,painted:await canvas.locator('path.leaflet-interactive').count()});
     await canvas.screenshot({path:path.join(output,`rower-${width}-${bike.id}.png`)});
    }
    assert.match(await page.locator('#rower-cycle-timi-12 .cycling-map__unavailable').innerText(),/Brak potwierdzonego śladu/);
    assert.equal(await page.locator('#cycling a[href$=".gpx"]').evaluateAll(links=>new Set(links.map(a=>a.href)).size),2);
    assert.equal(await page.locator('#cycling a[download]').count(),0);
    assert.equal(await page.locator('#cycling [data-map-day]').count(),0);
   }finally{await context.close();}
  }
  // Actual 7 GPX and 2 embedded bike previews with the network disconnected.
  for(const width of [390,1440]){
   const context=await browser.newContext({viewport:{width,height:950},reducedMotion:'reduce'});await instrument(context);
   try{
    const page=await context.newPage();await page.goto(url,{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.querySelector('[data-offline-status]')?.textContent.startsWith('Plan zapisany offline'),null,{timeout:60000});
    await context.setOffline(true);await page.reload({waitUntil:'networkidle'});await mainReady(page);
    assert.equal((await snapshot(page)).routes.length,7);
    assert(await page.locator('[data-map-offline]').first().isVisible());await capture(page,`offline-${width}`);
    await page.locator('details.route-details').evaluateAll(items=>items.forEach(e=>e.open=true));
    for(const r of tracks){
     const body=await page.evaluate(async f=>await (await fetch(f)).text(),r.gpx.path);assert.equal(sha(Buffer.from(body)),r.gpx.sha256);
     await page.locator(`[data-map-route="${r.id}"]`).click();await page.waitForTimeout(100);
     const state=await snapshot(page);assert.deepEqual(state.routes.map(t=>t.id),[r.id]);assert(state.routes[0].d && state.routes[0].d!=='M0 0');
     const [download]=await Promise.all([page.waitForEvent('download'),page.locator(`a[download][href="${r.gpx.path}"]`).click()]);
     const dest=path.join(output,`offline-${width}-${download.suggestedFilename()}`);await download.saveAs(dest);assert.equal(sha(fs.readFileSync(dest)),r.gpx.sha256);
     if(['TR-APHRODITE','TR-ARTEMIS'].includes(r.id))await capture(page,`offline-${width}-${r.id}`);
    }
    for(const b of plan.cycling_options.options.filter(b=>b.map.status==='preview')){
     const c=page.locator(`[data-cycling-map="${b.id}"]`);await c.scrollIntoViewIfNeeded();await page.waitForFunction(id=>document.querySelector(`[data-cycling-map="${id}"]`).dataset.mapReady==='true',b.id);
     const points=await page.evaluate(id=>{const m=window.__maps.find(m=>m.getContainer().dataset.cyclingMap===id);const lines=[];m.eachLayer(l=>{if(l instanceof L.Polyline)lines.push(l.getLatLngs().map(p=>[p.lat,p.lng]));});return lines;},b.id);
     assert.deepEqual(points,[b.map.points]);
    }
    evidence['offline'+width]={points:50,hikingGpx:7,cyclingPreviews:2,fullCyclingGpx:0,pass:true};
   }finally{await context.close();}
  }
  for(const [label,override] of [['http',{status:503}],['xml',{type:'application/gpx+xml',body:'<gpx>bad xml'}]]){
   overrides.set('/'+subpath+tracks[0].gpx.path,override);
   const context=await browser.newContext({serviceWorkers:'block',viewport:{width:390,height:950},reducedMotion:'reduce'});await instrument(context);
   try{
    const page=await context.newPage();await page.goto(url,{waitUntil:'networkidle'});await page.locator('#map-canvas').scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector('[data-map-routes-status]').textContent.includes('Aphrodite solo: błąd wczytania GPX'));
    assert.equal(await page.locator('[data-gpx-route="TR-APHRODITE"]').count(),0);assert.equal((await snapshot(page)).ids.length,50);
    await capture(page,`blad-${label}-390`);evidence['error-'+label]={fallback:true,points:50,pass:true};
   }finally{overrides.clear();await context.close();}
  }
  // Missing coordinates must remain in the full day count and place cards.
  // This fixture exists only in the HTTP response; canonical data stays intact.
  const fixture=structuredClone(plan);fixture.places.find(p=>p.id==='POI-NEOPHYTOS').coordinates=null;
  const sourceHtml=fs.readFileSync(path.join(root,'index.html'),'utf8');
  overrides.set('/'+subpath,{type:'text/html',body:sourceHtml.replace(/(<script type="application\/json" id="cypr-data">)[\s\S]*?(<\/script>)/,
   (_,a,b)=>a+JSON.stringify(fixture).replace(/<\//g,'<\\/')+b)});
  const fixtureContext=await browser.newContext({serviceWorkers:'block',viewport:{width:390,height:950},reducedMotion:'reduce'});await instrument(fixtureContext);
  try{
   const page=await fixtureContext.newPage();await page.goto(url,{waitUntil:'networkidle'});await mainReady(page);
   await page.locator('.map-filter__chip[data-map-day="06"]').click();const state=await snapshot(page);
   assert.equal(state.cards.length,5);assert.equal(state.ids.length,4);assert.match(state.status,/4 z 5 miejsc/);assert.match(state.status,/Bez współrzędnych: 1/);
   evidence.missingCoordinateCounter={pass:true,status:state.status,cards:5,pins:4};
   await page.locator('.map-tools').screenshot({path:path.join(output,'licznik-brak-wspolrzednych-fixture.png')});
  }finally{overrides.clear();await fixtureContext.close();}
  assert.equal(evidence.errors.length,0);
  console.log('PASS: 390/1440 · 50 points · 7 day filters with options · 7 painted/downloaded GPX · 2 bike previews · offline · HTTP/XML errors · keyboard');
 }catch(error){evidence.failures.push(error.stack);console.error(error);process.exitCode=1;}
 finally{fs.writeFileSync(path.join(output,'dowody-przegladarka.json'),JSON.stringify(evidence,null,2));await browser.close();await new Promise(resolve=>server.close(resolve));console.log('Artifacts:',output);}
})();

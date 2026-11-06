/* Rebuild both PDFs from the generated HTML. Requires npm install. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');

(async () => {
  const {server, url} = await require('./local_server.cjs')(root);
  let browser;
  try {
    browser = await chromium.launch({headless:true, ...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {channel:'chrome'})});
    const page = await browser.newPage({serviceWorkers:'block'});
    for (const [html, pdf] of [['index.html','cypr2026-print.pdf'],['cypr2026-handbook.html','cypr2026-handbook.pdf']]) {
      await page.goto(url + html, {waitUntil:'networkidle'});
      await page.emulateMedia({media:'print'});
      await page.evaluate(async () => {
        document.querySelectorAll('details').forEach(el => {el.open = true;});
        document.querySelectorAll('.photo--lead img').forEach(img => {img.loading = 'eager';});
        await document.fonts.ready;
        await Promise.all(Array.from(document.querySelectorAll('.photo--lead img')).map(img => img.decode().catch(() => {})));
      });
      const version = JSON.parse(fs.readFileSync(path.join(root,'data/Cypr_2026_zrodlo_prawdy.json'),'utf8')).meta.version;
      await page.pdf({path:path.join(root,pdf),format:'A4',printBackground:false,displayHeaderFooter:true,
        headerTemplate:'<span></span>',footerTemplate:`<div style="font:8px Arial;width:100%;text-align:center">Cypr 2026 · ${version} · <span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
        margin:{top:'12mm',right:'13mm',bottom:'15mm',left:'13mm'},preferCSSPageSize:true});
      console.log(`PDF: ${pdf} (${fs.statSync(path.join(root,pdf)).size} B)`);
    }
    const data = JSON.parse(fs.readFileSync(path.join(root,'data/Cypr_2026_zrodlo_prawdy.json'),'utf8'));
    const index = fs.readFileSync(path.join(root,'index.html'),'utf8');
    const sha256 = Object.fromEntries(['index.html','cypr2026-handbook.html','cypr2026-print.pdf','cypr2026-handbook.pdf'].map(file=>[file,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')]));
    fs.writeFileSync(path.join(root,'data/exports.json'),JSON.stringify({version:data.meta.version,canonical:index.match(/<link rel="canonical" href="([^"]+)"/)[1],sha256},null,2)+'\n');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {console.error(error);process.exitCode=1;});

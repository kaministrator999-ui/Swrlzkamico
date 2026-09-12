#!/usr/bin/env node
import fs from 'node:fs';

const page = fs.readFileSync(new URL('../web/collector.html', import.meta.url), 'utf8');
const manifest = JSON.parse(fs.readFileSync(new URL('../runtime_pages/manifest.json', import.meta.url), 'utf8'));
const index = fs.readFileSync(new URL('../runtime_pages/index.html', import.meta.url), 'utf8');
const scripts = [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match => match[1]).join('\n');
const ids = [...page.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);

new Function(scripts);
if (new Set(ids).size !== ids.length) throw new Error('collector console contains duplicate element IDs');
if (!page.includes('<title>SWRLZ Frozen Web Collector</title>')) throw new Error('stable page title marker is missing');
if (/<script[^>]+src=|<link[^>]+href=/i.test(page)) throw new Error('collector console must not depend on external page assets');
if (/innerHTML|outerHTML|insertAdjacentHTML/.test(scripts)) throw new Error('collector console contains an unsafe dynamic HTML sink');
if (/localStorage/.test(scripts) || !/sessionStorage/.test(scripts)) throw new Error('admin token must be session-scoped');

for (const id of ['statusPill','sourceForm','searchForm','frontierTable','trainingList','snapshotList','configForm','tokenDialog']) {
  if (!ids.includes(id)) throw new Error(`required console surface is missing: ${id}`);
}
for (const endpoint of ['readiness','status','action','search?','document?','snapshots','snapshot?']) {
  if (!scripts.includes(endpoint)) throw new Error(`collector API binding is missing: ${endpoint}`);
}
for (const action of ['start','pause','continue','step','seal','add-source','remove-source','configure','review','storage-check']) {
  if (!page.includes(action)) throw new Error(`collector action is missing: ${action}`);
}
if (!/respectRobots:true/.test(scripts) || !page.includes('Robots.txt compliance is enforced')) {
  throw new Error('fixed robots compliance is not represented in the console');
}
if (manifest.version < 4 || manifest.routes?.['/collector']?.source !== 'web/collector.html') {
  throw new Error('runtime route manifest does not own /collector');
}
if (!index.includes("['Frozen Web Collector','/collector']")) throw new Error('runtime launchpad does not link the collector');

console.log(`Frozen Web Collector console verification: PASS (${ids.length} unique IDs)`);
console.log('Verified runtime route ownership, safe rendering, session-only authorization, controls, API bindings, and launchpad discovery.');

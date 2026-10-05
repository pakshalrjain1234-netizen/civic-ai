import {cp, mkdir, readFile, writeFile, readdir, rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const target = path.join(root, 'build');
const development = process.argv.includes('--development');
const endpoint = process.env.VITE_AI_API_URL || (development ? 'http://127.0.0.1:8000' : '');
if (!endpoint) throw new Error('Set VITE_AI_API_URL to the deployed HTTPS Render URL before building.');
const url = new URL(endpoint);
if (url.pathname !== '/' || url.search || url.hash || url.username || url.password) throw new Error('VITE_AI_API_URL must be an API origin without a path, query or credentials.');
if (!development && (url.protocol !== 'https:' || ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) throw new Error('Production AI API must use a public HTTPS origin.');
if (development && !['http:', 'https:'].includes(url.protocol)) throw new Error('Invalid development API protocol.');
await rm(target, {recursive:true, force:true});
await mkdir(target, {recursive:true});
await cp(path.join(root, 'dist'), target, {recursive:true});
await writeFile(path.join(target, 'vision-env.js'), 'window.CIVICEYE_VISION_ENV = ' + JSON.stringify({visionApiUrl:url.origin, production:!development, frameIntervalMs:700}) + ';\n');
// Strip the legacy development-only Connections hostname literal from production.
if (!development) {
  const file = path.join(target, 'live-scan.js');
  await writeFile(file, (await readFile(file, 'utf8')).replace("['localhost','127.0.0.1']", '[location.hostname]'));
}
const files = (await readdir(target, {recursive:true})).filter(f => /\.(?:html|js|css|svg|png|webmanifest)$/.test(f) && f !== 'sw.js').sort();
const hash = createHash('sha256');
for (const file of files) hash.update(file).update(await readFile(path.join(target,file)));
const version = hash.digest('hex').slice(0,16);
const swPath = path.join(target, 'sw.js');
await writeFile(swPath, (await readFile(swPath, 'utf8')).replace('civiceye-shell-development', `civiceye-shell-${version}`));
const report = {mode:development?'development':'production', apiOrigin:url.origin, cacheVersion:version, publishDirectory:'build'};
await writeFile(path.join(root,'build-report.json'), JSON.stringify(report,null,2));
console.log(JSON.stringify(report));

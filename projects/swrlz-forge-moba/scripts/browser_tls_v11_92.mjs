// Optional managed-environment bridge: remote JavaScript still passes curl's
// system-CA TLS verification. Ordinary browsers keep their normal HTTPS path.
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const run=promisify(execFile);
export async function installSystemCATransport(page){
 if(process.env.SWYRL_TEST_CURL_TLS!=='1')return;
 await page.route('https://cdn.jsdelivr.net/**',async route=>{
  const url=new URL(route.request().url());
  if(url.protocol!=='https:'||url.hostname!=='cdn.jsdelivr.net')throw Error('Unexpected test CDN origin');
  const {stdout}=await run('curl',['--fail','--silent','--show-error','--location','--max-time','60','--proto','=https','--proto-redir','=https',url.href],{maxBuffer:10000000});
  await route.fulfill({status:200,contentType:'application/javascript',body:stdout});
 });
}

/* §E v11.492 — native ZIP model update reader.
 * No external scripts, no remote upload or filename-based project matching.
 * Inflate a single JSON member in memory and reuse the existing selected-card
 * identity, UV, rig, revision and compare-and-swap validation. */
const se492ModelUpload=(()=>{
 'use strict';
 const MAX_BYTES=32*1024*1024,MAX_ENTRIES=256;
 const decoder=new TextDecoder('utf-8',{fatal:true});
 const fail=message=>{throw Error('ZIP update: '+message)};
 const table=new Uint32Array(256);
 for(let n=0;n<256;n++){let c=n;for(let i=0;i<8;i++)c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);table[n]=c>>>0}
 function crc32(bytes){
  let c=0xffffffff;
  for(let i=0;i<bytes.length;i++)c=table[(c^bytes[i])&255]^(c>>>8);
  return (c^0xffffffff)>>>0;
 }
 async function inflate(bytes,expected){
  if(typeof DecompressionStream!=='function')
   fail('This browser cannot decompress ZIP files. Update the browser or use an uncompressed .swyrl.json.');
  let reader;
  try{reader=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader();}
  catch{fail('This browser cannot read raw ZIP deflate. Update the browser.')}
  const blocks=[];let length=0;
  try{
   while(true){
    const {done,value}=await reader.read();
    if(done)break;
    length+=value.byteLength;
    if(length>expected||length>MAX_BYTES){
     await reader.cancel().catch(()=>{});
     fail('Decompressed model exceeds its declared length or 32 MiB.');
    }
    blocks.push(value);
   }
  }catch(error){if(String(error.message||error).startsWith('ZIP update:'))throw error;fail('Compressed model data is damaged or unsupported.')}
  if(length!==expected)fail('Decompressed length does not match ZIP metadata.');
  const out=new Uint8Array(length);let offset=0;
  for(const block of blocks){out.set(block,offset);offset+=block.byteLength}
  return out;
 }
 function verifyName(name){
  if(!name||name.length>256||name.includes('\\')||name.startsWith('/')||
     name.split('/').some(p=>p==='..'||p==='.')||/[\u0000-\u001f]/.test(name))
   fail('Unsafe or invalid member path.');
 }
 async function zip(file,notice){
  const buf=await file.arrayBuffer(),view=new DataView(buf),bytes=new Uint8Array(buf),size=buf.byteLength;
  const u16=p=>view.getUint16(p,true),u32=p=>view.getUint32(p,true);
  if(size<22||size>MAX_BYTES)fail('Archive must be between 22 bytes and 32 MiB.');
  let eocd=-1;
  for(let i=size-22;i>=Math.max(0,size-22-65535);i--){
   if(u32(i)===0x06054b50&&i+22+u16(i+20)===size){eocd=i;break;}
  }
  if(eocd<0)fail('ZIP central directory not found.');
  if(u16(eocd+4)!==0||u16(eocd+6)!==0||u16(eocd+8)!==u16(eocd+10))
   fail('Multi-disk archives are not supported.');
  const count=u16(eocd+10),cdSize=u32(eocd+12),cdOffset=u32(eocd+16);
  if(!count||count>MAX_ENTRIES||cdOffset===0xffffffff||cdSize===0xffffffff||
     cdOffset+cdSize>eocd)fail('Invalid ZIP directory or too many entries.');
  const json=[],swyr=[];
  let cursor=cdOffset;
  for(let i=0;i<count;i++){
   if(cursor+46>cdOffset+cdSize||u32(cursor)!==0x02014b50)fail('Invalid ZIP directory entry.');
   const flags=u16(cursor+8),method=u16(cursor+10),checksum=u32(cursor+16),
    compressed=u32(cursor+20),uncompressed=u32(cursor+24),
    nameSize=u16(cursor+28),extraSize=u16(cursor+30),commentSize=u16(cursor+32),
    offset=u32(cursor+42),end=cursor+46+nameSize+extraSize+commentSize;
   if(end>cdOffset+cdSize)fail('Truncated ZIP directory.');
   const name=decoder.decode(bytes.subarray(cursor+46,cursor+46+nameSize));
   verifyName(name);
   cursor=end;
   if(name.endsWith('/')||name.startsWith('__MACOSX/'))continue;
   if(!/\.json$/i.test(name))continue;
   if(flags&1||flags&0x40)fail('Encrypted model archives are not supported.');
   if((flags&0x800)===0&&name.split('').some(ch=>ch.charCodeAt(0)>127))
    fail('Non-UTF-8 ZIP entry names are not supported.');
   if(![0,8].includes(method))fail('JSON member compression method is unsupported.');
   if(compressed>MAX_BYTES||uncompressed>MAX_BYTES||offset===0xffffffff)
    fail('JSON model exceeds the 32 MiB size limit or uses ZIP64.');
   const entry={name,method,compressed,uncompressed,checksum,offset};
   json.push(entry);
   if(/\.swyrl\.json$/i.test(name))swyr.push(entry);
  }
  if(cursor!==cdOffset+cdSize)fail('ZIP directory length mismatch.');
  const eligible=swyr.length?swyr:json;
  if(!eligible.length)fail('No .swyrl.json or .json model file found.');
  if(eligible.length!==1)fail('Multiple JSON model files found. Archive must contain exactly one .swyrl.json model.');
  const chosen=eligible[0],start=chosen.offset;
  if(start+30>cdOffset||u32(start)!==0x04034b50)fail('Model member header is damaged.');
  if(u16(start+8)!==chosen.method)fail('ZIP compression metadata is inconsistent.');
  const payload=start+30+u16(start+26)+u16(start+28);
  if(payload+chosen.compressed>cdOffset)fail('Model member is truncated.');
  notice('Extracting '+chosen.name+' from ZIP…');
  const compressed=bytes.subarray(payload,payload+chosen.compressed);
  const plain=chosen.method===0?compressed:await inflate(compressed,chosen.uncompressed);
  if(plain.byteLength!==chosen.uncompressed||crc32(plain)!==chosen.checksum)
   fail('ZIP model failed checksum verification.');
  let parsed;
  try{parsed=JSON.parse(decoder.decode(plain))}
  catch{fail('Archive JSON is malformed or not UTF-8.')}
  return parsed;
 }
 async function parse(file,notice=()=>{}){
  if(!file||!Number.isFinite(file.size)||file.size>MAX_BYTES)
   throw Error('Update file exceeds 32 MiB.');
  const zipped=/\.zip$/i.test(String(file.name||''));
  if(zipped)return zip(file,notice);
  let parsed;
  try{parsed=JSON.parse(await file.text())}
  catch{throw Error('Not a valid model JSON file. Choose a native .swyrl.json or a ZIP containing one.')}
  return parsed;
 }
 return Object.freeze({parse,crc32});
})();
window.SWYRL_ENGINE_ZIP_UPDATES_492=se492ModelUpload;

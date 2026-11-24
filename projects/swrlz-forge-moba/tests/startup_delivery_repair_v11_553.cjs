'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const boot=fs.readFileSync(path.join(root,'runtime/user_project_default_boot_v11_184.js'),'utf8');
const startup=fs.readFileSync(path.join(root,'runtime/engine_account_start_delivery_v11_553.js'),'utf8');
const repair=fs.readFileSync(path.join(root,'scripts/delivery_account_startup_repair_v11_553.py'),'utf8');
const packing=fs.readFileSync(path.join(root,'scripts/package_static_delivery_v11_552.py'),'utf8');
new vm.Script(boot);
new vm.Script(startup);
assert(boot.includes('},11000);'),'The sealed historical default runtime must remain unchanged');
assert(!boot.includes('id:boot.id,pending:boot.pending'),'Historical receipt must remain sealed; delivery adds ID');
assert(startup.includes('const entry=automatic?(override||defaults()):(override||chosenRow());'),
 'Blank user selection must open current workspace, not silently retry a stale default');
assert(startup.includes("entry.source==='cloud'&&pending.loading!==true"),
 'Manual retries must not duplicate a loading native cloud operation');
assert(startup.includes('receipt.id===entry.id'),
 'A successful receipt must match the requested project identity');
assert(startup.includes("if(automatic&&receipt?.attempted"),
 'Automatic failure should remain recoverable instead of entering a retry loop');
assert(repair.includes('def apply(module):'),'Delivery patch must expose an auditable function');
assert(repair.includes('text.count(START) != 1')&&repair.includes('text.count(END) != 1'),
 'Guard against ambiguous root startup replacements');
assert(repair.includes('OLD_DEADLINE')&&repair.includes('OLD_RECEIPT'),
 'Patch must update deadline and receipt identity in the served module');
assert(packing.includes('account_repair(source_module)')&&packing.includes('accountStartupDeliveryRepair'),
 'Source-sealed package must actually apply the repair and record a receipt');
console.log('SE553_DELIVERY_ACCOUNT_RECOVERY_PASS signed-in-loader=true default-id=true no-premature-deadline=true explicit-workspace=true');

// Regression: native Chat sidebar is a view, not a Redis storage mutation.
// Run with: node tests/test_native_chat_order_v211.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html=readFileSync(new URL("../chat/§wyrlz/index.html",import.meta.url),"utf8");
const start=html.indexOf("      const orderNativeThreads = threads => {");
const end=html.indexOf("      const renderThreads = () => {",start);
assert.ok(start>=0&&end>start,"Expected bounded ordering helper in canonical Chat");
assert.match(html,/const newestFirst=orderNativeThreads\(chatThreads\)/);
assert.match(html,/draftThread \? \[\{id:"__draft__".*\.\.\.newestFirst\]/);
const script=html.slice(start,end).replace("const orderNativeThreads =","globalThis.orderNativeThreads =");
const box={};
vm.runInNewContext(script,box);
const order=box.orderNativeThreads;
assert.equal(typeof order,"function");

const threads=[
 {id:"older",createdAt:100,messages:[{createdAt:200}]},
 {id:"recent",createdAt:500,messages:[{createdAt:520}]},
 {id:"updated-old",createdAt:150,messages:[{createdAt:850}]},
 {id:"pin",pinned:true,createdAt:80,messages:[{createdAt:130}]}
];
assert.deepEqual(Array.from(order(threads),t=>t.id),
 ["pin","updated-old","recent","older"],
 "Pinned threads precede descending most recent message activity");
assert.deepEqual(threads.map(t=>t.id),["older","recent","updated-old","pin"],
 "Ordering must not alter canonical source array");
assert.deepEqual(Array.from(order([
 {id:"z",createdAt:500,messages:[]},{id:"a",createdAt:500,messages:[]}
]),t=>t.id),["a","z"],"Identical activity has deterministic tie ordering");
assert.deepEqual(Array.from(order([
 {id:"invalid",createdAt:"invalid",messages:[]},{id:"valid",createdAt:1,messages:[]}
]),t=>t.id),["valid","invalid"]);
console.log("Native Chat newest-first drawer view and stable chronology tests passed");

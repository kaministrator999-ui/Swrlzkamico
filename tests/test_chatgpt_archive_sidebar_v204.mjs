// Synthetic/no-user-data DOM integration regression for the v204 archive drawer.
// Executes the real production adapter without installing jsdom or reaching a network.
"use strict";
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

class Node {
  constructor(tag = "div") {
    this.tag = tag;
    this.id = "";
    this.className = "";
    this._text = "";
    this.children = [];
    this.parent = null;
    this.dataset = {};
    this.attrs = {};
    this.listeners = {};
    this.style = {};
    this.disabled = false;
    this.scrollTop = 0;
    this._classes = new Set();
    this.classList = {
      contains: name => this._classes.has(name) || this.className.split(/\s+/).includes(name),
      toggle: (name, flag) => {
        const next = flag === undefined ? !this.classList.contains(name) : !!flag;
        if (next) this._classes.add(name);
        else this._classes.delete(name);
        return next;
      }
    };
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(""); }
  set innerHTML(value) { this._html = String(value); this.children = []; }
  get innerHTML() { return this._html || ""; }
  appendChild(node) {
    if (node.tag === "#fragment") {
      for (const child of [...node.children]) this.appendChild(child);
      return node;
    }
    if (node.parent) node.parent.children = node.parent.children.filter(x => x !== node);
    this.children.push(node); node.parent = this; return node;
  }
  append(...nodes) { nodes.forEach(n => this.appendChild(n)); }
  insertBefore(node, sibling) {
    if (node.parent) node.parent.children = node.parent.children.filter(x => x !== node);
    const i = this.children.indexOf(sibling);
    this.children.splice(i >= 0 ? i : this.children.length, 0, node);
    node.parent = this; return node;
  }
  after(node) {
    assert(this.parent);
    this.parent.insertBefore(node, this.parent.children[this.parent.children.indexOf(this) + 1] || null);
  }
  replaceChildren(...nodes) {
    this.children.forEach(n => { n.parent = null; });
    this.children = []; this._text = ""; nodes.forEach(n => this.appendChild(n));
  }
  remove() {
    if (this.parent) this.parent.children = this.parent.children.filter(x => x !== this);
    this.parent = null;
  }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  getAttribute(name) { return this.attrs[name]; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  click() { for (const fn of this.listeners.click || []) fn(); }
  querySelectorAll(selector) {
    assert(selector.startsWith("."));
    const wanted = selector.slice(1);
    const found = [];
    const scan = n => { for (const c of n.children) {
      if (c.className.split(/\s+/).includes(wanted)) found.push(c);
      scan(c);
    }};
    scan(this); return found;
  }
}

async function test() {
  const body = new Node("body"), head = new Node("head");
  const header = new Node("div"), title = new Node("div"), nativeList = new Node("div");
  const viewport = new Node("main"), nativeMessages = new Node("div");
  const menu = new Node("button"), accountAction = new Node("button");
  const newThread = new Node("button"), composer = new Node("form");
  header.className = "thread-panel-head";
  title.className = "thread-panel-title";
  title.textContent = "Chats";
  nativeList.id = "threadList"; viewport.id = "chatViewport";
  nativeMessages.id = "messageList"; menu.id = "menuButton";
  accountAction.id = "accountAction"; newThread.id = "newThreadButton";
  composer.id = "composerShell";
  const oldThread = new Node("div"); oldThread.textContent = "Native §wyrlz chat";
  nativeList.appendChild(oldThread);
  header.append(title, newThread);
  body.append(header, nativeList, viewport, menu, accountAction, composer);
  viewport.appendChild(nativeMessages);
  const document = {
    body, head, readyState: "complete",
    createElement: name => new Node(name),
    createDocumentFragment: () => new Node("#fragment"),
    querySelector: selector => selector === ".thread-panel-head" ? header :
      selector === ".thread-panel-title" ? title : null,
    getElementById: id => {
      const traverse = node => {
        if (node.id === id) return node;
        for (const child of node.children) {
          const found = traverse(child);
          if (found) return found;
        }
        return null;
      };
      return traverse(body);
    }
  };
  let mode = "allowed";
  const calls = [];
  const fetch = async (url, options) => {
    calls.push({url, options});
    if (mode === "deny") return {ok:false,status:401};
    if (url.includes("/list")) return {ok:true,json:async () => ({
      total:2556,nextOffset:30,items:[
        {id:"conv-alpha-0001",title:"Synthetic Alpha",messageCount:2,updatedAt:1760000000},
        {id:"conv-beta-0002",title:"Synthetic Beta",messageCount:1,updatedAt:1760000100}
      ]
    })};
    if (url.includes("/thread/")) return {ok:true,json:async () => ({
      id:"conv-alpha-0001",title:"Synthetic Alpha",
      messages:[{id:"m1",role:"user",text:"<script>literal private message</script>"},
                {id:"m2",role:"assistant",text:"Safe reply"}]
    })};
    throw Error("Unexpected endpoint " + url);
  };
  const context = {document, fetch, console, Number, String, Error, Date};
  vm.runInNewContext(fs.readFileSync(
    "chat/§wyrlz/assets/chatgpt-archive-sidebar-v204.js","utf8"
  ), context, {filename:"chatgpt-archive-sidebar-v204.js"});
  const tick = async () => { for (let i=0;i<8;i++) await Promise.resolve(); };
  const toggle = document.getElementById("cgaArchiveSwitch");
  assert(toggle, "document-arrow-up toggle must exist");
  assert(toggle.innerHTML.includes("<svg"), "document/upload icon should be a real SVG");
  assert.strictEqual(toggle.getAttribute("aria-pressed"), "false");
  assert.strictEqual(nativeList.children[0], oldThread);
  toggle.click();
  await tick();
  assert(body.classList.contains("cga-archive-mode"));
  assert.strictEqual(toggle.getAttribute("aria-pressed"), "true");
  assert.strictEqual(title.textContent, "Imported chats");
  const archiveList = document.getElementById("cgaSidebarList");
  assert(archiveList.textContent.includes("2556 saved ChatGPT conversations"));
  assert(archiveList.textContent.includes("Synthetic Alpha"));
  const row = archiveList.querySelectorAll(".cga-imported-row")[0];
  row.click();
  await tick();
  const reader = document.getElementById("cgaMainReader");
  assert(reader.textContent.includes("Synthetic Alpha"));
  assert(reader.textContent.includes("<script>literal private message</script>"));
  assert.strictEqual(reader.querySelectorAll(".cga-reader-message").length, 2);
  assert.strictEqual(row.getAttribute("aria-current"), "true");
  assert(calls.every(c => c.options.credentials === "same-origin"));
  assert(calls.every(c => c.options.cache === "no-store"));
  assert(calls.every(c => !c.options.method || c.options.method === "GET"));
  toggle.click();
  assert(!body.classList.contains("cga-archive-mode"));
  assert.strictEqual(title.textContent, "Chats");
  assert.strictEqual(nativeList.children[0], oldThread, "native list must remain intact");
  assert.strictEqual(nativeMessages.children.length, 0, "native transcript untouched");
  assert.strictEqual(reader.children.length, 0, "private imported reader cleared on exit");
  mode = "deny";
  toggle.click();
  await tick();
  assert(archiveList.textContent.includes("Sign in with your Google account"));
  accountAction.click();
  assert(!body.classList.contains("cga-archive-mode"), "signing out must clear imported view");
  console.log("v204 PASS: document-arrow toggle, read-only safe transcript, native isolation, pagination view, Google gate");
}
test().catch(e => {console.error(e); process.exitCode = 1;});

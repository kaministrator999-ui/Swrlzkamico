/* Explicit, read-only ChatGPT archive import in the existing Chat settings shell. */
(() => {
  "use strict";
  function el(tag, className, label) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (label !== undefined) node.textContent = label;
    return node;
  }
  function init() {
    const nav = document.querySelector(".settings-nav");
    const main = document.querySelector(".settings-main");
    if (!nav || !main || document.getElementById("chatgptImportNav")) return;
    const style = el("style");
    style.textContent = `
      .cga-control {display:block;width:100%;box-sizing:border-box;min-width:0;margin:9px 0;padding:10px;
        color:#e9faff;background:rgba(5,29,48,.78);border:1px solid rgba(126,214,255,.28);border-radius:10px}
      .cga-action {padding:9px 12px;margin:5px 7px 5px 0;border-radius:9px;cursor:pointer;
        background:rgba(14,75,96,.78);border:1px solid rgba(126,214,255,.3);color:#edfbff}
      .cga-action:disabled {opacity:.43;cursor:default}
      .cga-status {white-space:pre-wrap;font-size:11px;line-height:1.5;color:#b5deed;margin:10px 0;overflow-wrap:anywhere}
      .cga-list {margin-top:9px;display:grid;gap:7px}
      .cga-item {text-align:left;display:grid;gap:4px;width:100%;padding:10px;border-radius:9px;
        border:1px solid rgba(126,214,255,.15);background:rgba(9,34,52,.7);color:#e9faff;cursor:pointer}
      .cga-sub {font-size:10px;color:#9cb8c6}
      .cga-thread {max-height:49vh;overflow:auto;overflow-wrap:anywhere;margin:10px 0}
      .cga-msg {border-left:2px solid rgba(126,214,255,.28);padding:7px 9px;margin-bottom:9px;font-size:11px;
        white-space:pre-wrap;overflow-wrap:anywhere;background:rgba(3,22,38,.6);color:#e1f4ff}
      .cga-msg .cga-sub {display:block;margin-bottom:5px}
    `;
    document.head.appendChild(style);

    const button = el("button", "settings-nav-button", "ChatGPT imports");
    button.id = "chatgptImportNav";
    button.type = "button";
    button.dataset.settingsSection = "chatgpt-import";
    nav.appendChild(button);
    const pane = el("section", "settings-pane");
    pane.dataset.settingsPane = "chatgpt-import";
    pane.appendChild(el("h3", "", "Import ChatGPT conversations"));
    pane.appendChild(el("p", "settings-pane-lead",
      "Select your ChatGPT conversation export ZIP. This is a private, read-only archive tied to your signed-in Google account. Reimporting newer exports adds new messages without duplicating existing conversation IDs."));
    const file = el("input", "cga-control");
    file.type = "file";
    file.accept = ".zip,application/zip,application/x-zip-compressed";
    file.setAttribute("aria-label", "Choose ChatGPT exported conversation ZIP");
    pane.appendChild(file);
    const upload = el("button", "cga-action", "Import selected ZIP");
    upload.type = "button";
    pane.appendChild(upload);
    const refresh = el("button", "cga-action", "Refresh imported conversations");
    refresh.type = "button";
    pane.appendChild(refresh);
    const status = el("div", "cga-status", "Sign in with Google to store and view imported conversations.");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    pane.appendChild(status);
    pane.appendChild(el("p", "cga-sub",
      "Imports save visible user/assistant text only. Images, audio, hidden reasoning, attachments and alternate branches are not imported. Nothing is shared with models or training automatically."));
    const listing = el("div", "cga-list");
    pane.appendChild(listing);
    const pager = el("div");
    const previous = el("button", "cga-action", "Newer");
    const next = el("button", "cga-action", "Older");
    previous.type = next.type = "button";
    pager.append(previous, next);
    pane.appendChild(pager);
    const thread = el("div", "cga-thread");
    pane.appendChild(thread);
    main.appendChild(pane);

    let busy = false;
    let offset = 0;
    let nextOffset = null;
    let total = 0;
    const setBusy = (value) => {
      busy = value;
      upload.disabled = refresh.disabled = value;
      file.disabled = value;
    };
    async function jsonFetch(url) {
      const response = await fetch(url, {credentials:"same-origin", cache:"no-store"});
      if (!response.ok) throw Error(response.status === 401
        ? "Sign in with Google first." : "Archive unavailable (HTTP " + response.status + ").");
      return response.json();
    }
    async function showThread(id) {
      thread.replaceChildren();
      try {
        const data = await jsonFetch("/api/chatgpt_archive/thread/" + encodeURIComponent(id));
        thread.appendChild(el("h4", "", data.title));
        for (const m of data.messages || []) {
          const card = el("div", "cga-msg");
          card.appendChild(el("span", "cga-sub", m.role === "user" ? "You" : "ChatGPT"));
          card.appendChild(el("div", "", m.text));
          thread.appendChild(card);
        }
        thread.scrollTop = 0;
      } catch (error) { status.textContent = error.message; }
    }
    async function load() {
      if (busy) return;
      listing.replaceChildren();
      thread.replaceChildren();
      try {
        const data = await jsonFetch("/api/chatgpt_archive/list?offset=" + offset + "&limit=30");
        nextOffset = data.nextOffset;
        total = data.total;
        status.textContent = total
          ? total + " imported conversations stored privately on the server."
          : "No imported conversations yet. Select a ChatGPT export ZIP above.";
        for (const item of data.items) {
          const row = el("button", "cga-item");
          row.type = "button";
          row.appendChild(el("strong", "", item.title));
          const when = item.updatedAt ? new Date(item.updatedAt * 1000).toLocaleDateString() : "Date unknown";
          row.appendChild(el("span", "cga-sub", item.messageCount + " text messages · " + when));
          row.addEventListener("click", () => showThread(item.id));
          listing.appendChild(row);
        }
        previous.disabled = offset === 0;
        next.disabled = nextOffset === null;
      } catch (error) {
        status.textContent = error.message;
        previous.disabled = next.disabled = true;
      }
    }
    button.addEventListener("click", () => {
      document.querySelectorAll(".settings-nav-button").forEach(n => n.classList.toggle("active", n === button));
      document.querySelectorAll(".settings-pane").forEach(n => n.classList.toggle("active", n === pane));
      offset = 0;
      load();
    });
    refresh.addEventListener("click", () => {offset=0;load();});
    previous.addEventListener("click", () => {offset=Math.max(0,offset-30);load();});
    next.addEventListener("click", () => {if(nextOffset!==null){offset=nextOffset;load();}});
    upload.addEventListener("click", async () => {
      const selected = file.files && file.files[0];
      if (!selected || !selected.name.toLowerCase().endsWith(".zip")) {
        status.textContent = "Choose a ChatGPT export ZIP first.";
        return;
      }
      if (selected.size > 110 * 1024 * 1024) {
        status.textContent = "This ZIP exceeds the 110 MiB upload limit.";
        return;
      }
      setBusy(true);
      status.textContent = "Uploading and indexing your ZIP… keep this page open. Progress will appear as messages are committed.";
      try {
        const response = await fetch("/api/chatgpt_archive/import", {
          method:"POST", credentials:"same-origin",
          headers:{"Content-Type":"application/zip","X-Swrlz-Import":"1"},
          body:selected
        });
        if (!response.ok || !response.body) throw Error(
          response.status===401 ? "Sign in with Google first." :
          "Import request failed (HTTP " + response.status + ").");
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let pending = "";
        let terminal = false;
        const handle = (line) => {
          if (!line.trim()) return;
          const event = JSON.parse(line);
          if (event.type === "PROGRESS") status.textContent =
            "Indexed " + event.conversations + " conversations · new: " + event.created +
            " · updated: " + event.updated + " · already present: " + event.skipped +
            " · newly added messages: " + event.addedMessages +
            " · unsupported/empty: " + event.unsupported;
          if (event.type === "COMPLETE") {
            terminal = true;
            status.textContent = "Import complete: " + event.created + " new conversations, " +
              event.updated + " updated, " + event.skipped + " unchanged, " +
              event.addedMessages + " newly added messages, " +
              event.unsupported + " empty or non-text-only conversations skipped.";
          }
          if (event.type === "ERROR") throw Error(event.message || "Import interrupted; reselect the same ZIP to resume.");
        };
        while (true) {
          const result = await reader.read();
          if (result.done) break;
          pending += decoder.decode(result.value, {stream:true});
          let newline;
          while ((newline = pending.indexOf("\n")) >= 0) {
            const line = pending.slice(0, newline);
            pending = pending.slice(newline + 1);
            handle(line);
          }
        }
        if (pending.trim()) handle(pending);
        if (!terminal) throw Error("Upload stopped before completion. Reimport the same ZIP to resume; already saved messages will not duplicate.");
      } catch (error) {
        status.textContent = error.message || "Import interrupted; reselect this ZIP to resume.";
      } finally {
        setBusy(false);
        if (status.textContent.startsWith("Import complete")) {
          const receipt = status.textContent;
          offset=0;
          await load();
          status.textContent = receipt + "\n" + total + " total imported conversations.";
        }
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, {once:true});
  else init();
})();

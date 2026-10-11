/* v204: imported ChatGPT archive is a separate read-only browsing mode.
   Native §wyrlz thread state, composer, station polling and Settings importer
   remain owned by their existing components. */
(() => {
  "use strict";
  const mk = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const init = () => {
    const header = document.querySelector(".thread-panel-head");
    const title = document.querySelector(".thread-panel-title");
    const nativeList = document.getElementById("threadList");
    const viewport = document.getElementById("chatViewport");
    const nativeMessages = document.getElementById("messageList");
    const menuButton = document.getElementById("menuButton");
    const accountAction = document.getElementById("accountAction");
    if (!header || !title || !nativeList || !viewport || !nativeMessages ||
        document.getElementById("cgaArchiveSwitch")) return;

    const style = mk("style");
    style.textContent = [
      ".cga-head-pair{display:flex;align-items:center;gap:9px;min-width:0}",
      ".cga-switch{display:inline-grid;place-items:center;width:35px;height:35px;flex:0 0 35px;padding:0;",
      "border:1px solid rgba(95,192,255,.38);border-radius:11px;background:rgba(8,39,61,.75);",
      "color:#d7f6ff;cursor:pointer;touch-action:manipulation}",
      ".cga-switch svg{display:block;width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.7;",
      "stroke-linecap:round;stroke-linejoin:round}",
      ".cga-switch[aria-pressed=true]{border-color:rgba(56,232,255,.85);color:#fff;",
      "background:linear-gradient(125deg,rgba(8,95,109,.9),rgba(41,49,109,.92))}",
      ".cga-switch:focus-visible,.cga-page button:focus-visible,.cga-imported-row:focus-visible{",
      "outline:2px solid #7de5ff;outline-offset:2px}",
      ".cga-sidebar-list{display:none}",
      "body.cga-archive-mode #threadList{display:none!important}",
      "body.cga-archive-mode #cgaSidebarList{display:block}",
      "body.cga-archive-mode #newThreadButton{display:none!important}",
      ".cga-page{display:flex;gap:6px;align-items:center;justify-content:space-between;padding:8px 3px;",
      "flex-wrap:wrap;color:#a8d6e5;font-size:11px}",
      ".cga-page button{min-height:37px;padding:7px 10px;color:#d9f6ff;",
      "border:1px solid rgba(95,192,255,.29);border-radius:10px;background:rgba(9,43,65,.72);cursor:pointer}",
      ".cga-page button:disabled{opacity:.4;cursor:default}",
      ".cga-imported-row{width:100%;text-align:left;cursor:pointer}",
      ".cga-imported-row[aria-current=true]{border-color:rgba(56,232,255,.65)}",
      ".cga-sidebar-note{padding:11px 9px;font-size:11px;color:#afc7d7;line-height:1.55;white-space:pre-wrap}",
      ".cga-main-reader{display:none;width:min(680px,100%);margin:0 auto;min-height:100%;color:#e6f6ff}",
      "body.cga-archive-mode #messageList{display:none!important}",
      "body.cga-archive-mode #cgaMainReader{display:block}",
      "body.cga-archive-mode #composerShell,body.cga-archive-mode #jumpLatest{display:none!important}",
      "body.cga-archive-mode #chatViewport{bottom:0!important}",
      ".cga-reader-heading{padding:13px 14px;margin-bottom:18px;border:1px solid rgba(95,192,255,.30);",
      "border-radius:15px;background:rgba(5,25,44,.86)}",
      ".cga-reader-heading h2{margin:7px 0 4px;font-size:20px;line-height:1.3;overflow-wrap:anywhere}",
      ".cga-reader-note{font-size:11px;color:#9acfe2;line-height:1.5}",
      ".cga-reader-message{padding:13px 15px;margin-bottom:13px;border:1px solid rgba(126,214,255,.18);",
      "border-radius:15px;background:rgba(5,25,44,.70);overflow-wrap:anywhere}",
      ".cga-reader-message[data-role=user]{margin-left:min(14%,70px);background:rgba(20,46,76,.72)}",
      ".cga-reader-role{display:block;margin-bottom:8px;font-size:11px;letter-spacing:.04em;",
      "font-weight:700;color:#9fe4fa}",
      ".cga-reader-text{font-size:14px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere}",
      ".cga-load-messages{display:block;margin:15px auto 25px;padding:10px 14px;min-height:40px;",
      "border:1px solid rgba(95,192,255,.4);border-radius:11px;background:rgba(11,50,71,.85);",
      "color:#e6faff;cursor:pointer}",
      "@media(max-width:600px){.cga-reader-heading{padding:11px}.cga-reader-message{padding:11px 12px}.cga-reader-text{font-size:13px}}",
      "@media(prefers-reduced-motion:reduce){.cga-switch{transition:none!important}}"
    ].join("\n");
    document.head.appendChild(style);

    const pair = mk("div", "cga-head-pair");
    header.insertBefore(pair, title);
    pair.appendChild(title);
    const toggle = mk("button", "cga-switch");
    toggle.type = "button";
    toggle.id = "cgaArchiveSwitch";
    toggle.setAttribute("aria-pressed", "false");
    toggle.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8l-6-8Z"/><path d="M13 3v6h6"/><path d="M11 18v-7m-3 3 3-3 3 3"/></svg>';
    pair.appendChild(toggle);

    const archiveList = mk("div", "thread-list cga-sidebar-list");
    archiveList.id = "cgaSidebarList";
    archiveList.setAttribute("aria-label", "Imported ChatGPT conversations");
    nativeList.after(archiveList);
    const reader = mk("section", "cga-main-reader");
    reader.id = "cgaMainReader";
    reader.setAttribute("aria-label", "Imported ChatGPT conversation · read only");
    viewport.appendChild(reader);

    let active = false, offset = 0, count = 0, nextOffset = null;
    let selectedId = "", listRequest = 0, readerRequest = 0;
    const PAGE_SIZE = 30;
    const PAGE_MESSAGES = 100;

    function syncButton() {
      toggle.setAttribute("aria-pressed", String(active));
      const action = active ? "Switch back to §wyrlz chats" : "Show imported ChatGPT conversations";
      toggle.setAttribute("aria-label", action);
      toggle.title = action;
      title.textContent = active ? "Imported chats" : "Chats";
      document.body.classList.toggle("cga-archive-mode", active);
    }

    function showPlaceholder(text) {
      reader.replaceChildren();
      const card = mk("div", "cga-reader-heading");
      card.appendChild(mk("div", "cga-reader-note", "📄 Imported ChatGPT archive · read only"));
      card.appendChild(mk("h2", "", text));
      card.appendChild(mk("p", "cga-reader-note",
        "Choose a conversation from the side menu. Imported messages are not sent to §wyrlz or mixed into native chat history."));
      reader.appendChild(card);
    }

    function closeMenu() {
      if (document.body.classList.contains("menu-open") && menuButton) menuButton.click();
    }

    async function fetchJSON(url) {
      const response = await fetch(url, {credentials: "same-origin", cache: "no-store"});
      if (!response.ok) {
        if (response.status === 401) throw Error("Sign in with your Google account to browse imported conversations.");
        throw Error("Imported archive unavailable (HTTP " + response.status + ").");
      }
      return response.json();
    }

    function pager(data) {
      const controls = mk("div", "cga-page");
      const older = mk("button", "", "Older →");
      older.type = "button";
      older.disabled = nextOffset === null;
      older.addEventListener("click", () => loadPage(nextOffset));
      const newer = mk("button", "", "← Newer");
      newer.type = "button";
      newer.disabled = offset === 0;
      newer.addEventListener("click", () => loadPage(Math.max(0, offset - PAGE_SIZE)));
      const showing = data.items.length ? (offset + 1) + "–" + (offset + data.items.length) :
        "0";
      controls.append(newer, mk("span", "", showing + " of " + count), older);
      return controls;
    }

    async function loadPage(nextPage = 0) {
      const request = ++listRequest;
      offset = Math.max(0, Number(nextPage) || 0);
      archiveList.replaceChildren(mk("div", "cga-sidebar-note", "Loading imported conversations…"));
      try {
        const data = await fetchJSON("/api/chatgpt_archive/list?offset=" + offset + "&limit=" + PAGE_SIZE);
        if (!active || request !== listRequest) return;
        count = Number(data.total || 0);
        nextOffset = Number.isInteger(data.nextOffset) ? data.nextOffset : null;
        archiveList.replaceChildren();
        archiveList.appendChild(mk("div", "cga-sidebar-note",
          count + " saved ChatGPT conversations · read only"));
        if (!count) {
          archiveList.appendChild(mk("div", "cga-sidebar-note",
            "No imported conversations yet. Open Settings → ChatGPT imports to upload an export."));
          return;
        }
        for (const item of (data.items || [])) {
          const row = mk("div", "thread-row");
          const select = mk("button", "thread-main cga-imported-row");
          select.type = "button";
          select.dataset.conversationId = String(item.id);
          select.setAttribute("aria-current", String(item.id === selectedId));
          select.appendChild(mk("span", "thread-title", item.title || "Untitled ChatGPT conversation"));
          const when = item.updatedAt ? new Date(item.updatedAt * 1000).toLocaleDateString() : "Date unknown";
          select.appendChild(mk("span", "thread-meta",
            (Number(item.messageCount || 0)) + " text messages · " + when));
          select.addEventListener("click", () => openThread(item.id));
          row.appendChild(select);
          archiveList.appendChild(row);
        }
        archiveList.appendChild(pager(data));
        archiveList.scrollTop = 0;
      } catch (error) {
        if (active && request === listRequest) {
          archiveList.replaceChildren(mk("div", "cga-sidebar-note", error.message));
        }
      }
    }

    async function openThread(id) {
      const request = ++readerRequest;
      selectedId = String(id);
      showPlaceholder("Loading conversation…");
      closeMenu();
      viewport.scrollTop = 0;
      try {
        const data = await fetchJSON("/api/chatgpt_archive/thread/" + encodeURIComponent(selectedId));
        if (!active || request !== readerRequest) return;
        const entries = Array.isArray(data.messages) ? data.messages : [];
        reader.replaceChildren();
        const heading = mk("div", "cga-reader-heading");
        heading.appendChild(mk("div", "cga-reader-note", "📄 Imported from ChatGPT · read only"));
        heading.appendChild(mk("h2", "", data.title || "Untitled ChatGPT conversation"));
        heading.appendChild(mk("div", "cga-reader-note",
          entries.length + " text messages · Original messages preserved; replying is not enabled in archive view."));
        reader.appendChild(heading);
        let cursor = 0;
        function appendNext() {
          const batch = document.createDocumentFragment();
          const ending = Math.min(entries.length, cursor + PAGE_MESSAGES);
          while (cursor < ending) {
            const message = entries[cursor++];
            const node = mk("article", "cga-reader-message");
            node.dataset.role = message.role === "user" ? "user" : "assistant";
            node.appendChild(mk("span", "cga-reader-role",
              message.role === "user" ? "You" : "ChatGPT"));
            node.appendChild(mk("div", "cga-reader-text", String(message.text || "")));
            batch.appendChild(node);
          }
          reader.appendChild(batch);
          if (cursor < entries.length) {
            const more = mk("button", "cga-load-messages", "Show next messages (" + cursor + " of " + entries.length + ")");
            more.type = "button";
            more.addEventListener("click", () => {
              more.remove();
              if (active && request === readerRequest) appendNext();
            });
            reader.appendChild(more);
          }
        }
        appendNext();
        viewport.scrollTop = 0;
        archiveList.querySelectorAll(".cga-imported-row").forEach(el => {
          const visibleId = el.dataset.conversationId;
          el.setAttribute("aria-current", String(visibleId === selectedId));
        });
      } catch (error) {
        if (active && request === readerRequest) showPlaceholder(error.message);
      }
    }

    function enterArchive() {
      active = true;
      selectedId = "";
      syncButton();
      showPlaceholder("Select an imported conversation");
      loadPage(0);
    }
    function leaveArchive() {
      active = false;
      listRequest++;
      readerRequest++;
      selectedId = "";
      syncButton();
      archiveList.replaceChildren();
      reader.replaceChildren();
      // Native Chat's message list and active thread are preserved untouched.
    }
    toggle.addEventListener("click", () => active ? leaveArchive() : enterArchive());
    if (accountAction) accountAction.addEventListener("click", () => {
      if (active) leaveArchive();
    }, {capture: true});
    syncButton();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, {once: true});
  } else {
    init();
  }
})();

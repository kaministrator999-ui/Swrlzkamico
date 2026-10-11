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
    const memoryControl = el("label", "cga-control");
    memoryControl.style.display = "flex";
    memoryControl.style.gap = "9px";
    memoryControl.style.alignItems = "center";
    const memoryEnabled = el("input");
    memoryEnabled.type = "checkbox";
    memoryEnabled.setAttribute("aria-label", "Use imported ChatGPT conversations as §wyrlz memory");
    memoryControl.append(memoryEnabled, el("span", "",
      "Let §wyrlz recall relevant details from my imported conversations"));
    pane.appendChild(memoryControl);
    const memoryStatus = el("div", "cga-status",
      "Imported memories are off until you enable them. No model weight training.");
    memoryStatus.setAttribute("role", "status");
    pane.appendChild(memoryStatus);
    async function refreshMemory() {
      try {
        const response = await fetch("/api/chatgpt_archive/memory",
          {credentials:"same-origin",cache:"no-store"});
        if (!response.ok) throw Error(response.status===401 ?
          "Sign in with Google to enable memory." : "Memory status HTTP "+response.status);
        const state = await response.json();
        memoryEnabled.checked = !!state.enabled;
        memoryStatus.textContent = !state.enabled
          ? "Off. Imported conversations stay private and read-only; §wyrlz does not retrieve them."
          : state.state === "ready"
            ? "Ready: " + state.indexed + " conversations indexed for private contextual recall."
            : state.state === "building"
              ? "Preparing private memory index on the server: " + state.indexed +
                " / " + state.total + ". This continues while you leave Chat."
              : state.state === "error"
                ? "Memory preparation interrupted. Switch off, then on to retry."
                : "Memory is enabled. Private indexing is queued.";
      } catch (err) { memoryStatus.textContent=err.message; }
    }
    memoryEnabled.addEventListener("change", async () => {
      const desired=!!memoryEnabled.checked;
      memoryEnabled.disabled=true;
      try {
        const res=await fetch("/api/chatgpt_archive/memory",{
          method:"POST",credentials:"same-origin",cache:"no-store",
          headers:{"Content-Type":"application/json","X-Swrlz-Import":"1"},
          body:JSON.stringify({enabled:desired})
        });
        if (!res.ok) throw Error("Could not save memory preference (HTTP "+res.status+").");
        await refreshMemory();
      } catch (err) {
        memoryEnabled.checked=!desired;
        memoryStatus.textContent=err.message;
      } finally { memoryEnabled.disabled=false; }
    });
    setInterval(() => {
      if (pane.classList.contains("active") && memoryEnabled.checked && !memoryEnabled.disabled)
        refreshMemory();
    }, 5000);
    const eraseAll = el("button", "cga-action", "Delete all imported conversations");
    eraseAll.type = "button";
    pane.appendChild(eraseAll);
    const status = el("div", "cga-status", "Sign in with Google to store and view imported conversations.");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    pane.appendChild(status);
    pane.appendChild(el("p", "cga-sub",
      "Imports save visible user/assistant text only. Images, audio, hidden reasoning, attachments and alternate branches are not imported. Relevant older excerpts may be used as model context only if you enable memory above; imported history is never used for weight training."));
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
    let pollTimer = null;
    let jobState = null;
    const uploadMarkerKey = "swrlz-chatgpt-upload-transfer-v2";
    function readMarker() {
      try { return JSON.parse(window.localStorage.getItem(uploadMarkerKey) || "null"); }
      catch (_) { return null; }
    }
    function saveMarker(value) {
      try {
        if (value) window.localStorage.setItem(uploadMarkerKey, JSON.stringify(value));
        else window.localStorage.removeItem(uploadMarkerKey);
      } catch (_) { /* Imports remain safe when browser storage is disabled. */ }
    }
    const setBusy = (value) => {
      busy = value;
      upload.disabled = refresh.disabled = eraseAll.disabled = value;
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
        const eraseOne = el("button", "cga-action", "Delete this imported conversation");
        eraseOne.type = "button";
        eraseOne.addEventListener("click", async () => {
          if (!window.confirm("Delete this imported ChatGPT conversation from your §wyrlz archive?")) return;
          try {
            const result = await fetch("/api/chatgpt_archive/thread/" + encodeURIComponent(id), {
              method:"DELETE", credentials:"same-origin", headers:{"X-Swrlz-Import":"1"}
            });
            if (!result.ok) throw Error("Deletion failed (HTTP " + result.status + ").");
            thread.replaceChildren();
            offset = 0;
            await load();
            status.textContent = "Imported conversation deleted from this account.";
          } catch (error) { status.textContent = error.message; }
        });
        thread.appendChild(eraseOne);
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
    async function checkJob() {
      if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
      if (busy) return;
      try {
        const previous = jobState && jobState.state;
        const job = await jsonFetch("/api/chatgpt_archive/status");
        jobState = job;
        const stored = Number(job.storedTotal || 0);
        if (job.state === "running") {
          status.textContent = "Server import continuing: " + job.conversations +
            " conversations processed · " + job.created + " new · " +
            job.updated + " updated · " + job.skipped + " already present · " +
            job.unsupported + " unsupported · " + stored +
            " total stored. You may leave this page and return; importing continues on the server.";
        } else if (job.state === "complete") {
          status.textContent = "Import complete: " + job.created + " new, " +
            job.updated + " updated, " + job.skipped + " unchanged · " +
            job.addedMessages + " messages added · " + job.unsupported +
            " non-text conversations skipped. " + stored + " total stored.";
        } else if (job.state === "error" || job.state === "interrupted") {
          status.textContent = "Import " + job.state + " after " +
            (job.conversations || 0) + " conversations. " + (job.message || "") +
            " " + stored + " conversations remain on the server. Reimporting this ZIP is safe.";
        } else {
          status.textContent = stored + " imported conversations stored on the server." +
            (readMarker() ? " An unfinished ZIP upload can resume when you reselect the same file." : "");
        }
        if (previous === "running" && job.state !== "running") {
          offset = 0;
          await load();
          // The list loader shows a generic count; retain the job receipt.
          if (job.state === "complete") status.textContent =
            "Import complete: " + job.created + " new, " + job.updated +
            " updated, " + job.skipped + " unchanged. " + stored + " total stored.";
        }
        if (job.state === "running" && pane.classList.contains("active")) {
          pollTimer = setTimeout(checkJob, 3000);
        }
      } catch (error) {
        status.textContent = "Could not refresh import progress: " + error.message +
          " Saved conversations are not deleted by a connection interruption.";
      }
    }
    button.addEventListener("click", () => {
      document.querySelectorAll(".settings-nav-button").forEach(n => n.classList.toggle("active", n === button));
      document.querySelectorAll(".settings-pane").forEach(n => n.classList.toggle("active", n === pane));
      offset = 0;
      load().then(checkJob);
      refreshMemory();
    });
    refresh.addEventListener("click", () => {offset=0;load().then(checkJob);refreshMemory();});
    eraseAll.addEventListener("click", async () => {
      if (busy || !window.confirm("Permanently delete ALL imported ChatGPT conversations from your §wyrlz account? Your native chats are not affected.")) return;
      if (!window.confirm("Confirm deletion of every imported ChatGPT archive conversation. This cannot be undone.")) return;
      setBusy(true);
      status.textContent = "Deleting your imported archive…";
      try {
        const response = await fetch("/api/chatgpt_archive", {
          method:"DELETE", credentials:"same-origin", headers:{"X-Swrlz-Import":"1"}
        });
        if (!response.ok) throw Error("Deletion failed (HTTP " + response.status + ").");
        const result = await response.json();
        offset = 0;
        listing.replaceChildren();
        thread.replaceChildren();
        status.textContent = "Deleted " + result.deleted + " imported conversations.";
      } catch (error) { status.textContent = error.message; }
      finally { setBusy(false); }
    });
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
      if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
      setBusy(true);
      let accepted = false;
      try {
        const uploadHeaders = {"X-Swrlz-Import":"1"};
        const fingerprint = {name:selected.name, size:selected.size, modified:selected.lastModified};
        const saved = readMarker();
        let transfer = null;
        if (saved && saved.name === fingerprint.name &&
            saved.size === fingerprint.size && saved.modified === fingerprint.modified &&
            /^[0-9a-f]{32}$/.test(saved.uploadId || "")) {
          try {
            const previous = await fetch("/api/chatgpt_archive/upload/" + saved.uploadId, {
              credentials:"same-origin", cache:"no-store"
            });
            if (previous.ok) {
              const found = await previous.json();
              if (found.size === selected.size) transfer = found;
            }
          } catch (_) { /* Resume discovery failed; restart only the transport. */ }
        }
        if (!transfer) {
          saveMarker(null);
          const started = await fetch("/api/chatgpt_archive/init", {
            method:"POST", credentials:"same-origin", cache:"no-store",
            headers:{...uploadHeaders, "Content-Type":"application/json"},
            body:JSON.stringify({size:selected.size})
          });
          if (!started.ok) throw Error(started.status === 409 ?
            "A server import is already running. Reopen this panel to view its progress." :
            "Cannot start import (HTTP " + started.status + ").");
          transfer = await started.json();
          saveMarker({...fingerprint, uploadId:transfer.uploadId});
        }
        if (!/^[0-9a-f]{32}$/.test(transfer.uploadId) ||
            !Number.isInteger(transfer.chunkSize) || transfer.chunkSize < 1024 ||
            transfer.chunkSize > 2 * 1024 * 1024 ||
            !Number.isInteger(transfer.received) || transfer.received < 0 ||
            transfer.received > selected.size) throw Error("Import server returned invalid upload instructions.");

        let sentBytes = transfer.received;
        while (sentBytes < selected.size) {
          const piece = selected.slice(sentBytes, Math.min(sentBytes + transfer.chunkSize, selected.size));
          let acknowledged = false;
          for (let attempt = 0; attempt < 3 && !acknowledged; attempt++) {
            try {
              const sent = await fetch("/api/chatgpt_archive/chunk/" + transfer.uploadId +
                "?offset=" + sentBytes, {
                method:"POST", credentials:"same-origin", cache:"no-store",
                headers:{...uploadHeaders, "Content-Type":"application/octet-stream"}, body:piece
              });
              if (!sent.ok) throw Error("ZIP chunk transfer HTTP " + sent.status);
              const ack = await sent.json();
              if (ack.received !== sentBytes + piece.size) throw Error("Upload chunk acknowledgment mismatch");
              sentBytes = ack.received;
              acknowledged = true;
            } catch (error) {
              // A received chunk might have lost only its response; ask the server
              // for its authoritative byte position rather than sending duplicates.
              const resumed = await fetch("/api/chatgpt_archive/upload/" + transfer.uploadId, {
                credentials:"same-origin", cache:"no-store"
              });
              if (!resumed.ok) throw Error("Upload session expired. Reselect this ZIP to restart safely.");
              const actual = await resumed.json();
              if (actual.received === sentBytes + piece.size) {
                sentBytes = actual.received;
                acknowledged = true;
              } else if (actual.received !== sentBytes || attempt === 2) {
                throw Error("Upload interrupted at " + Math.round(100 * sentBytes / selected.size) +
                  "%. Reselect this ZIP to resume from the server's saved offset.");
              }
            }
          }
          status.textContent = "Uploading ZIP: " + Math.round(100 * sentBytes / selected.size) +
            "% (" + Math.round(sentBytes / 1048576) + " / " +
            Math.round(selected.size / 1048576) + " MiB). You may resume after an interruption.";
        }
        status.textContent = "ZIP transferred. Starting a server-owned import job…";
        const response = await fetch("/api/chatgpt_archive/complete/" + transfer.uploadId, {
          method:"POST", credentials:"same-origin", cache:"no-store", headers:uploadHeaders
        });
        if (!response.ok) throw Error("Could not start background indexing (HTTP " + response.status + ").");
        const job = await response.json();
        if (job.state !== "running" && job.state !== "complete") throw Error("Invalid import job response");
        accepted = true;
        saveMarker(null);
        status.textContent = "Server import started. You can switch apps or return later; stored progress will remain visible.";
      } catch (error) {
        status.textContent = error.message || "Import interrupted. Previously stored conversations remain safe.";
      } finally {
        setBusy(false);
        if (accepted) {
          offset = 0;
          await load();
          await checkJob();
        }
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, {once:true});
  else init();
})();

/* Public release notes only. Preferences belong to this browser and exact update ID. */
(() => {
  'use strict';
  const opener = document.getElementById('chatUpdatesOpen');
  if (!opener || document.getElementById('chatUpdatesDialog')) return;
  const url = '/chat/§wyrlz/assets/chat-updates-v1.json';
  const hiddenKey = id => 'swrlz:chat-updates:hidden:' + id;
  const seenKey = id => 'swrlz:chat-updates:seen:' + id;
  const memorySeen = new Set();
  const read = (storage, key) => { try { return storage.getItem(key) === 'true'; } catch (_) { return false; } };
  const write = (storage, key, enabled) => { try { enabled ? storage.setItem(key, 'true') : storage.removeItem(key); return true; } catch (_) { return false; } };
  // Accessing a storage object itself can throw in restricted browsers.
  const local = {getItem: key => window.localStorage.getItem(key), setItem: (key, value) => window.localStorage.setItem(key, value), removeItem: key => window.localStorage.removeItem(key)};
  const session = {getItem: key => window.sessionStorage.getItem(key), setItem: (key, value) => window.sessionStorage.setItem(key, value), removeItem: key => window.sessionStorage.removeItem(key)};
  const node = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  const dialog = node('dialog', undefined, 'chat-updates-dialog');
  dialog.id = 'chatUpdatesDialog';
  dialog.setAttribute('aria-labelledby', 'chatUpdatesTitle');
  dialog.setAttribute('aria-describedby', 'chatUpdatesSubtitle');
  const header = node('header');
  const title = node('h2', 'Chat updates'); title.id = 'chatUpdatesTitle'; title.tabIndex = -1;
  const subtitle = node('p', 'Loading update notes…'); subtitle.id = 'chatUpdatesSubtitle';
  header.append(node('small', '§WYRLZ CHAT'), title, subtitle);
  const main = node('section', undefined, 'chat-updates-content');
  const status = node('p', '', 'chat-updates-status'); status.setAttribute('role', 'status');
  const latestList = node('ul'); latestList.id = 'chatUpdatesLatest';
  const history = node('details'); history.id = 'chatUpdatesHistory';
  const historySummary = node('summary', 'Previous updates');
  const historyList = node('div');
  const coverage = node('p', '', 'chat-updates-coverage');
  history.append(historySummary, coverage, historyList);
  main.append(status, latestList, history);
  const footer = node('footer');
  const label = node('label');
  const hide = node('input'); hide.type = 'checkbox'; hide.id = 'chatUpdatesHide';
  label.append(hide, document.createTextNode(' Don’t show again for this update'));
  const retry = node('button', 'Retry'); retry.type = 'button'; retry.hidden = true;
  const close = node('button', 'Continue'); close.type = 'button'; close.id = 'chatUpdatesClose';
  footer.append(label, retry, close); dialog.append(header, main, footer); document.body.append(dialog);
  let data = null, pending = false, fetching = null, deferred = null, returnFocus = null, closingRecord = null;
  const suppressed = id => read(local, hiddenKey(id));
  const seen = id => memorySeen.has(id) || read(session, seenKey(id));
  const remember = id => { memorySeen.add(id); write(session, seenKey(id), true); };
  const appendList = (parent, changes) => {
    for (const change of changes) parent.append(node('li', change));
  };
  const validRecord = record => record && typeof record.id === 'string' && /^[a-zA-Z0-9._-]{1,120}$/.test(record.id)
    && typeof record.title === 'string' && record.title.length <= 1000
    && typeof record.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(record.date)
    && Array.isArray(record.changes) && record.changes.length > 0 && record.changes.length <= 100
    && record.changes.every(change => typeof change === 'string' && change.length <= 16000);
  const validate = value => value?.schema === 'swrlz-chat-updates-v1' && validRecord(value.latest)
    && Array.isArray(value.history) && value.history.length <= 1000 && value.history.every(validRecord)
    && new Set([value.latest.id, ...value.history.map(record => record.id)]).size === value.history.length + 1;
  const render = () => {
    title.textContent = 'What’s new in Chat';
    subtitle.textContent = data.latest.title + ' · ' + data.latest.date;
    latestList.replaceChildren(); appendList(latestList, data.latest.changes);
    historySummary.textContent = 'All previous recorded updates · ' + data.history.length;
    coverage.textContent = data.historyCoverage?.description || 'Earlier recorded Chat updates.';
    historyList.replaceChildren();
    for (const record of data.history) {
      const details = node('details'); details.className = 'chat-updates-entry';
      const summary = node('summary', (record.version ? record.version + ' · ' : '') + record.title);
      const when = node('p', record.date + (record.kind ? ' · ' + record.kind : ''), 'chat-updates-date');
      const list = node('ul'); appendList(list, record.changes); details.append(summary, when, list); historyList.append(details);
    }
    hide.disabled = false; hide.checked = suppressed(data.latest.id);
    status.textContent = ''; retry.hidden = true;
    dialog.dataset.updateId = data.latest.id;
  };
  const open = () => {
    if (data) render();
    if (!dialog.open) { returnFocus = document.activeElement; dialog.showModal(); close.focus(); }
    pending = false; opener.textContent = 'Chat updates';
  };
  const occupied = () => closingRecord || document.hidden || document.querySelector('dialog[open]')
    || document.querySelector('#topEdge[data-state="busy"]')
    || document.body.classList.contains('settings-open') || document.body.classList.contains('work-open')
    || (document.activeElement?.matches('textarea, input, [contenteditable="true"]') && String(document.activeElement.value || document.activeElement.textContent || '').trim().length > 0);
  const maybeOpen = () => {
    clearTimeout(deferred); deferred = null;
    if (!pending || !data || suppressed(data.latest.id) || seen(data.latest.id)) return;
    if (occupied()) { deferred = setTimeout(maybeOpen, 1000); return; }
    open();
  };
  const refresh = () => {
    if (fetching) return fetching;
    fetching = (async () => {
      try {
        const response = await fetch(url, {cache: 'no-store', credentials: 'same-origin', signal: AbortSignal.timeout(15000)});
        if (!response.ok) throw new Error('Update notes unavailable');
        const value = await response.json();
        if (!validate(value)) throw new Error('Invalid update notes');
        const changed = value.latest.id !== data?.latest.id;
        data = value;
        if (dialog.open) render();
        if (changed && !suppressed(data.latest.id) && !seen(data.latest.id)) {
          pending = !dialog.open; opener.textContent = pending ? 'Chat updates · New' : 'Chat updates';
          if (pending) maybeOpen();
        }
      } catch (_) {
        if (dialog.open) { status.textContent = 'Couldn’t load Chat updates. Try again when connected.'; retry.hidden = false; }
      } finally { fetching = null; }
    })();
    return fetching;
  };
  hide.disabled = true;
  hide.addEventListener('change', () => {
    if (dialog.dataset.updateId && !write(local, hiddenKey(dialog.dataset.updateId), hide.checked)) status.textContent = 'This browser couldn’t save the preference. You can still close these notes for this session.';
  });
  const closeDialog = () => {
    if (!dialog.open) return;
    closingRecord = {id: dialog.dataset.updateId, checked: hide.checked, focus: returnFocus};
    // Native close events are queued. Save now so an immediate reload cannot lose dismissal.
    if (closingRecord.id) {
      write(local, hiddenKey(closingRecord.id), closingRecord.checked);
      remember(closingRecord.id);
    }
    dialog.close();
  };
  close.addEventListener('click', closeDialog);
  dialog.addEventListener('cancel', event => { event.preventDefault(); closeDialog(); });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopPropagation(); closeDialog(); return;
    }
    if (event.key !== 'Tab') return;
    const controls = [...dialog.querySelectorAll('button:not([disabled]), input:not([disabled]), summary, a[href], [tabindex]:not([tabindex="-1"])')]
      .filter(element => !element.hidden && element.getClientRects().length > 0);
    const first = controls[0], last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
  });
  dialog.addEventListener('close', () => {
    const closed = closingRecord || {id: dialog.dataset.updateId, checked: hide.checked, focus: returnFocus};
    closingRecord = null;
    if (closed.id) { write(local, hiddenKey(closed.id), closed.checked); remember(closed.id); }
    if (closed.focus?.isConnected && !closed.focus.closest('[aria-hidden="true"], [inert]')) closed.focus.focus();
    else document.getElementById('menuButton')?.focus();
    if (pending) setTimeout(maybeOpen, 0);
  });
  opener.setAttribute('aria-haspopup', 'dialog');
  opener.addEventListener('click', () => { open(); refresh(); });
  retry.addEventListener('click', refresh);
  window.addEventListener('focus', () => { if (!document.hidden) refresh(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { refresh(); maybeOpen(); } });
  document.addEventListener('focusout', () => { if (pending) setTimeout(maybeOpen, 0); });
  setInterval(() => { if (!document.hidden) refresh(); }, 120000);
  refresh();
})();

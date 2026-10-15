/* v260 · Structured GitHub operation summaries, no token or HTML injection. */
(() => {
  'use strict';
  const make = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };
  const integer = x => Number.isSafeInteger(x) && x >= 0 ? x : null;
  const fileLink = value => typeof value === 'string'
    && /^https:\/\/github\.com\/kaministrator999-ui\/Swrlzing-core\/blob\/main\/write-action-tests\/[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.txt$/.test(value)
    && !value.includes('..') ? value : null;
  const commitLink = value => typeof value === 'string'
    && /^https:\/\/github\.com\/kaministrator999-ui\/Swrlzing-core\/commit\/[a-fA-F0-9]{40}$/.test(value) ? value : null;
  const addMetric = (grid,label,value,variant) => {
    if (value === null || value === undefined) return;
    const cell=make('div','github-work-metric'+(variant?' '+variant:''));
    cell.append(make('span','github-work-metric-label',label),
                make('strong','github-work-metric-value',value));
    grid.append(cell);
  };
  function render(host,widget) {
    if (!host || !widget || widget.contract !== 'swrlz-widget-v1' || widget.kind !== 'github-work') return false;
    const d=widget.data || {};
    if (d.operation !== 'CREATE_FILE' || d.repo !== 'kaministrator999-ui/Swrlzing-core'
        || d.branch !== 'main' || d.verification !== 'EXACT_BYTES_MATCHED') return false;
    const path = String(d.path || '');
    if (!/^write-action-tests\/[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.txt$/.test(path) || path.includes('..')) return false;
    const file = fileLink(d.fileUrl);
    if (!file) return false;
    const card = make('div','github-work-dashboard');
    card.setAttribute('aria-label','Verified GitHub work summary');
    const summary = make('div','github-work-summary');
    const heading = make('div','github-work-heading');
    heading.append(make('div','github-work-eyebrow','GitHub · Work receipt'),
                   make('strong','github-work-title','File created'));
    summary.append(heading,make('span','github-work-verified','✓ Exact bytes verified'));
    card.append(summary);
    const repoLine = make('div','github-work-repo','kaministrator999-ui / Swrlzing-core · main');
    const fileRow = make('a','github-work-file',path);
    fileRow.href=file;fileRow.target='_blank';fileRow.rel='noopener noreferrer';
    card.append(repoLine,fileRow);
    const grid=make('div','github-work-metrics');
    addMetric(grid,'Files created',integer(d.filesCreated));
    addMetric(grid,'Bytes written',integer(d.bytesWritten));
    addMetric(grid,'Text lines',integer(d.textLines));
    const confirmed = d.providerStatsAvailable===true
       && integer(d.additions)!==null && integer(d.deletions)!==null;
    if (confirmed) {
      addMetric(grid,'Added lines','+'+integer(d.additions),'added');
      addMetric(grid,'Deleted lines','−'+integer(d.deletions),'deleted');
      addMetric(grid,'Files changed',integer(d.filesChanged));
    }
    card.append(grid);
    const footer=make('div','github-work-footer');
    const commit=commitLink(d.commitUrl);
    if (commit) {
      const anchor=make('a','github-work-commit','Commit '+String(d.commitSha||'').slice(0,7));
      anchor.href=commit;anchor.target='_blank';anchor.rel='noopener noreferrer';footer.append(anchor);
    }
    footer.append(make('span','github-work-stat-note',
      confirmed ? 'Commit diff statistics verified with GitHub' :
        'Commit diff statistics unavailable · verified file metrics shown'));
    if (typeof d.commitAt==='string' && !Number.isNaN(Date.parse(d.commitAt))) {
      footer.append(make('time','github-work-when',new Date(d.commitAt).toLocaleString()));
    }
    card.append(footer);
    host.append(card);
    return true;
  }
  window.SwrlzGithubWorkView = Object.freeze({render});
})();
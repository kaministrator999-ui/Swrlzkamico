import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { execFileSync } from 'node:child_process';

const ORIGIN = 'https://swrlzkamico-o3nu.vercel.app';
const STATE_PATH = 'swrlz/collector/control/state.json';

export function adminCredentialState(value) {
  const token = String(value || '').trim();
  if (!token) return 'unavailable';
  // Vercel intentionally exports this marker for non-readable sensitive values.
  // It is never an application credential and must not be sent as one.
  if (token === '[SENSITIVE]') return 'redacted';
  return 'available';
}

export async function verifyLive({ token, expected, fetcher = fetch }) {
  assert.equal(adminCredentialState(token), 'available', 'The application credential is not available to this verification job.');
  assert.match(expected.engineSha256, /^[a-f0-9]{64}$/);
  assert.match(expected.collectorVersion, /^\d+\.\d+\.\d+$/);
  const api = async (path, body) => {
    const response = await fetcher(`${ORIGIN}/api/collector/${path}`, {
      method: body ? 'POST' : 'GET',
      headers: {
        'x-swrlz-admin-token': token,
        'cache-control': 'no-store',
        ...(body ? { 'content-type': 'application/json' } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
      redirect: 'error',
      signal: AbortSignal.timeout(45000),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      const failure = new Error(`${path}: HTTP ${response.status}; ${payload.error?.code || 'REQUEST_FAILED'}; ${payload.error?.message || 'request rejected'}`);
      failure.apiPath = path;
      failure.httpStatus = response.status;
      throw failure;
    }
    return payload;
  };
  const readiness = await api('readiness');
  assert.equal(readiness.host.sourceSha256, expected.engineSha256, 'Live engine differs from the verified source.');
  assert.equal(readiness.module.version, expected.collectorVersion);
  assert.equal(readiness.storage.configured, true);
  assert.equal(readiness.storage.access, 'private');
  assert.equal(readiness.host.deploymentRequiredForRuntimeChanges, false);
  const before = await api('status');
  assert.equal(before.module.sha256, expected.engineSha256);
  assert.notEqual(before.state.status, 'running', 'Collection is running; this job will not interrupt it.');
  assert(!before.state.sealIntentAt || before.state.status === 'sealed', 'Sealing is in progress.');

  // An empty patch saves the current server configuration. It cannot replay
  // stale settings from the preceding GET or change any collection policy.
  const saved = await api('action', { action: 'configure', config: {} });
  assert.equal(saved.module.sha256, expected.engineSha256);
  assert(saved.state.stateRevision > before.state.stateRevision, 'The durable revision did not advance.');
  for (const key of ['config', 'sources', 'snapshotId', 'status', 'totals', 'trainingQueue']) {
    assert(isDeepStrictEqual(saved.state[key], before.state[key]), `${key} changed during verification.`);
  }
  const reloaded = await api('status');
  assert.equal(reloaded.module.sha256, expected.engineSha256);
  assert.equal(reloaded.state.stateRevision, saved.state.stateRevision, 'The confirmed revision did not survive a fresh read.');
  for (const key of ['config', 'sources', 'snapshotId', 'status', 'totals', 'trainingQueue']) {
    assert(isDeepStrictEqual(reloaded.state[key], saved.state[key]), `${key} changed after the save.`);
  }
  return {
    ok: true,
    scope: 'production-collector-api',
    collectorVersion: expected.collectorVersion,
    engineSha256: expected.engineSha256,
    beforeRevision: before.state.stateRevision,
    savedRevision: saved.state.stateRevision,
    reloadedRevision: reloaded.state.stateRevision,
    configurationUnchanged: true,
    statePersisted: true,
    collectionStatus: reloaded.state.status,
    documents: reloaded.state.totals.documents,
    sources: reloaded.state.sources.length,
    trainingAccepted: reloaded.state.totals.trainingAccepted,
  };
}

async function compareStorageVersions() {
  const token = process.env.BLOB_READ_WRITE_TOKEN;
  if (!token) return { available: false };
  const storeId = token.split('_')[3];
  assert.match(storeId || '', /^[A-Za-z0-9]+$/);
  const metadataResponse = await fetch(`https://vercel.com/api/blob?url=${encodeURIComponent(STATE_PATH)}`, {
    headers: { authorization: `Bearer ${token}`, 'x-api-version': '12', 'x-vercel-blob-store-id': storeId },
    redirect: 'error', signal: AbortSignal.timeout(20000),
  });
  const metadata = metadataResponse.ok ? await metadataResponse.json() : {};
  const delivery = await fetch(`https://${storeId}.private.blob.vercel-storage.com/${STATE_PATH}?cache=0`, {
    headers: { authorization: `Bearer ${token}` }, redirect: 'error', signal: AbortSignal.timeout(20000),
  });
  const deliveryEtag = delivery.headers.get('etag');
  await delivery.arrayBuffer();
  return {
    available: true,
    metadataStatus: metadataResponse.status,
    deliveryStatus: delivery.status,
    metadataEtagPresent: Boolean(metadata.etag),
    deliveryEtagPresent: Boolean(deliveryEtag),
    etagsEqual: Boolean(metadata.etag && metadata.etag === deliveryEtag),
    metadataEtagWeak: String(metadata.etag || '').startsWith('W/'),
    deliveryEtagWeak: String(deliveryEtag || '').startsWith('W/'),
  };
}

function safeMessage(error) {
  let message = String(error?.message || 'Verification failed.');
  // Redact before truncation, including any credential embedded in an error.
  for (const value of Object.values(process.env).filter(value => value && value.length >= 8).sort((a, b) => b.length - a.length)) {
    message = message.replaceAll(value, '[redacted]');
  }
  return message.slice(0, 500);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const expected = JSON.parse(await readFile('.collector/VERIFY_REQUEST.json', 'utf8'));
    console.log(JSON.stringify({ storageVersionCheck: await compareStorageVersions() }));
    let credentialState = adminCredentialState(process.env.SWRLZ_ADMIN_TOKEN);
    console.log(JSON.stringify({ applicationCredential: credentialState }));
    let receipt;
    if (credentialState === 'available') {
      try {
        receipt = await verifyLive({ token: process.env.SWRLZ_ADMIN_TOKEN, expected });
      } catch (error) {
        // Only an authentication rejection before any mutation may select the
        // separately authorized Blob check. Never replay a failed write.
        if (error.apiPath !== 'status' || error.httpStatus !== 401) throw error;
        credentialState = 'rejected-before-write';
        console.log(JSON.stringify({ applicationCredential: credentialState, apiWriteAttempted: false }));
      }
    }
    if (!receipt) {
      let output;
      try {
        output = execFileSync('python3', ['scripts/verify_collector_storage.py'], {
        encoding: 'utf8', timeout: 180000, maxBuffer: 100000,
        // The storage check has its own existing resource credential. It neither
        // reads nor changes the application's administrator credential.
        env: {
          PATH: process.env.PATH,
          BLOB_READ_WRITE_TOKEN: process.env.BLOB_READ_WRITE_TOKEN || '',
          PYTHONDONTWRITEBYTECODE: '1',
        },
        stdio: ['ignore', 'pipe', 'pipe'],
        });
      } catch (error) {
        let failure;
        try { failure = JSON.parse(error.stdout || '{}'); } catch { /* No private process output is logged. */ }
        throw new Error(failure?.error || 'The production storage verification process failed.');
      }
      receipt = { ...JSON.parse(output), applicationCredential: credentialState, apiWriteVerified: false };
    }
    console.log(JSON.stringify(receipt));
  } catch (error) {
    console.error(JSON.stringify({ ok: false, error: safeMessage(error) }));
    process.exitCode = 1;
  }
}

const test = require('node:test');
const assert = require('node:assert/strict');
const waitForPagesArtifact = require('../.github/scripts/wait-for-pages-artifact.cjs');

function fixture(responses) {
  let calls = 0;
  const waits = [];
  return {
    github: {rest: {actions: {listWorkflowRunArtifacts: async (params) => {
      assert.deepEqual(params, {owner: 'merelyer', repo: 'aitoolpilot', run_id: 37891456925});
      return {data: {artifacts: responses[Math.min(calls++, responses.length - 1)]}};
    }}}},
    context: {repo: {owner: 'merelyer', repo: 'aitoolpilot'}, runId: 37891456925},
    core: {info() {}},
    sleep: async (ms) => waits.push(ms),
    waits,
    calls: () => calls,
  };
}

test('waits for an uploaded artifact to become visible', async () => {
  const f = fixture([[], [{name: 'github-pages', expired: false}]]);
  await waitForPagesArtifact(f);
  assert.equal(f.calls(), 2);
  assert.deepEqual(f.waits, [5000]);
});

test('fails after bounded retries when the Pages artifact is absent or expired', async () => {
  const f = fixture([[{name: 'other', expired: false}, {name: 'github-pages', expired: true}]]);
  await assert.rejects(waitForPagesArtifact(f), /github-pages/);
  assert.equal(f.calls(), 12);
  assert.equal(f.waits.length, 11);
});

test('does not hide API permission failures', async () => {
  const f = fixture([]);
  f.github.rest.actions.listWorkflowRunArtifacts = async () => {throw new Error('403');};
  await assert.rejects(waitForPagesArtifact(f), /403/);
  assert.equal(f.waits.length, 0);
});

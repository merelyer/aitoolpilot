module.exports = async function waitForPagesArtifact({
  github, context, core,
  sleep = ms => new Promise(resolve => setTimeout(resolve, ms)),
}) {
  for (let attempt = 1; attempt <= 12; attempt++) {
    const {data} = await github.rest.actions.listWorkflowRunArtifacts({
      ...context.repo,
      run_id: context.runId,
    });
    if (data.artifacts.some(artifact => artifact.name === 'github-pages' && !artifact.expired)) {
      core.info('github-pages is visible to the Actions REST API.');
      return;
    }
    core.info(`Waiting for github-pages metadata (${attempt}/12).`);
    if (attempt < 12) await sleep(5000);
  }
  throw new Error('github-pages was not visible after 12 checks; refusing to deploy.');
};

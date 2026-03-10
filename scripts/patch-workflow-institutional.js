const fs = require('fs');
const path = require('path');

const workflowPath = path.join(__dirname, '..', 'outputs', 'n8n-workflow-csp-daily-scan.json');
const nodesPath = path.join(__dirname, '..', 'temp-institutional-nodes.json');

const workflow = JSON.parse(fs.readFileSync(workflowPath, 'utf8'));
const newNodes = JSON.parse(fs.readFileSync(nodesPath, 'utf8'));

// Find index of "Fetch Options Chains" and "CSP Opportunity Scorer"
const fetchChainsIdx = workflow.nodes.findIndex(n => n.name === 'Fetch Options Chains');
const scorerIdx = workflow.nodes.findIndex(n => n.name === 'CSP Opportunity Scorer');
if (fetchChainsIdx === -1 || scorerIdx === -1) {
  console.error('Could not find Fetch Options Chains or CSP Opportunity Scorer');
  process.exit(1);
}

// Insert the two new nodes after Fetch Options Chains (before Scorer)
workflow.nodes.splice(fetchChainsIdx + 1, 0, ...newNodes);

// Add connections: Filter Earnings -> Fetch Full Chains; Fetch Full Chains -> Institutional Signals; Institutional Signals -> Scorer
const conn = workflow.connections;
conn['Filter Earnings Conflicts'].main[0].push(
  { node: 'Fetch Full Chains (Institutional)', type: 'main', index: 0 }
);
conn['Fetch Full Chains (Institutional)'] = { main: [[{ node: 'Institutional Signals', type: 'main', index: 0 }]] };
conn['Institutional Signals'] = { main: [[{ node: 'CSP Opportunity Scorer', type: 'main', index: 0 }]] };

// Scorer currently has one input from Fetch Options Chains. We need Scorer to run when BOTH Fetch Options Chains AND Institutional Signals have run.
// So we add Institutional Signals -> CSP Opportunity Scorer. n8n will run Scorer when both inputs have data. But Fetch Options Chains -> Scorer already exists.
// So we only need to add Institutional Signals -> Scorer. The Scorer will be triggered by the last of the two (depending on execution order). Actually in n8n, a node with two incoming connections runs when it has received data from all incoming connections. So we're good - we added Institutional Signals -> Scorer. Fetch Options Chains -> Scorer was already there. So Scorer runs when both have produced output.

fs.writeFileSync(workflowPath, JSON.stringify(workflow, null, 2));
console.log('Inserted 2 nodes and added connections. Now update Scorer/Format/Sheets manually or via search_replace.');

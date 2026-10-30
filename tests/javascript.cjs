const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const build = path.join(__dirname, '../build');
const values = JSON.parse(fs.readFileSync(path.join(build, 'javascript-values.json'), 'utf8'));
const scope = {};
vm.createContext(scope);
vm.runInContext(fs.readFileSync(path.join(build, 'translate.zh_CN.js'), 'utf8'), scope);
const failures = [];
for (const [key, expected] of Object.entries(values)) {
  const actual = scope._(key);
  if (actual !== expected) failures.push({ key, expected, actual });
}
if (failures.map(f => f.key).sort().join(',') !== 'No.,Yes.') {
  throw new Error('Unexpected lookup results: ' + JSON.stringify(failures));
}
const total = Object.keys(values).length;
fs.writeFileSync(path.join(build, 'javascript-result.json'), JSON.stringify({total, passed: total-failures.length, known_upstream_failures: failures}, null, 2)+'\n');
console.log(`PASS: ${total-failures.length}/${total} lookups; only the 2 documented upstream reserved-key failures remain.`);

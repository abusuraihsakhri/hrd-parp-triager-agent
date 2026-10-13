"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("web/index.html", "utf8");
const js = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(js, "Inline JavaScript found");
new vm.Script(js[1], {filename: "web/index.html"});

const elements = new Map();
function get(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      value: "", textContent: "", style: {}, checked: false, disabled: false,
      handlers: {},
      addEventListener(type, handler) { this.handlers[type] = handler; }
    });
  }
  return elements.get(id);
}
const document = {
  getElementById: get,
  createElement() { return {click() {}, remove() {}}; },
  body: {appendChild() {}}
};
const sandbox = {
  document, JSON, Number, Blob, URL: {createObjectURL: () => "blob:demo", revokeObjectURL() {}},
  setTimeout(cb) { cb(); }
};
vm.runInNewContext(js[1], sandbox);
function submit() {
  get("audit-form").handlers.submit({preventDefault() {}});
  const output = get("output").textContent;
  return output.startsWith("{") ? JSON.parse(output) : null;
}
get("nominal").handlers.click();
let value = submit();
assert.equal(value.overall_urgency, "ROUTINE");
assert.equal(value.total_alerts, 0);
assert.equal(value.audit_hash, undefined);
get("critical-example").handlers.click();
value = submit();
assert.equal(value.overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(value.total_alerts, 3);
get("critical").checked = false;
value = submit();
assert.equal(value.overall_urgency, "ELEVATED_RISK");
assert.equal(value.critical_alerts_count, 0);
get("primary").value = "NaN";
const prior = get("tasks").textContent;
submit();
assert.equal(get("tasks").textContent, prior);
assert.match(get("form-error").textContent, /finite numeric/);
get("primary").value = "12";
get("task-id").value = "<img src=x onerror=alert(1)>";
value = submit();
assert.equal(value.task_id, "<img src=x onerror=alert(1)>");
assert.equal(html.includes("innerHTML"), false);
assert.equal(html.includes("fetch('/api/audit'"), false);
console.log("Browser-only demonstration: syntax, nominal/elevated/critical, validation and text rendering passed.");

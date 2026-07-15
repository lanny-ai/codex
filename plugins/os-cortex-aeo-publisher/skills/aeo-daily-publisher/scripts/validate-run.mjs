#!/usr/bin/env node
import fs from "node:fs";

const file = process.argv[2];
if (!file) throw new Error("Usage: validate-run.mjs <run.json>");
const run = JSON.parse(fs.readFileSync(file, "utf8"));
const failures = [];
if (!run.gates || typeof run.gates !== "object") failures.push("gates:missing");
for (const [name, passed] of Object.entries(run.gates ?? {})) if (passed !== true) failures.push(`gate:${name}`);
if ((run.status === "published" || run.publishedUrl) && failures.length) failures.push("publication:failed-gates");
if (run.status === "published" && !/^https:\/\//.test(run.publishedUrl ?? "")) failures.push("publishedUrl:invalid");
process.stdout.write(`${JSON.stringify({ ok: failures.length === 0, failures, file }, null, 2)}\n`);
if (failures.length) process.exit(1);

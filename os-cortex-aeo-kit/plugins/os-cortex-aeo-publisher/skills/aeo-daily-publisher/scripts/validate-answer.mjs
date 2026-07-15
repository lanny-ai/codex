#!/usr/bin/env node
import fs from "node:fs";

const file = process.argv[2];
if (!file) throw new Error("Usage: validate-answer.mjs <answer.json>");
const answer = JSON.parse(fs.readFileSync(file, "utf8"));
const required = ["slug","question","title","description","summary","publishedAt","updatedAt","author","reviewer","cluster","originalInsight","sections","claims","sources","relatedSlugs","cta"];
const failures = [];
for (const field of required) if (answer[field] === undefined || answer[field] === null || answer[field] === "") failures.push(`missing:${field}`);
const words = String(answer.summary ?? "").trim().split(/\s+/).filter(Boolean).length;
if (words > 100) failures.push("summary:over-100-words");
if (!Array.isArray(answer.sources) || new Set(answer.sources.map((source) => source.url)).size < 3) failures.push("sources:fewer-than-3-unique");
if (!Array.isArray(answer.sections) || answer.sections.length < 3) failures.push("sections:fewer-than-3");
if (String(answer.originalInsight ?? "").trim().split(/\s+/).length < 20) failures.push("originalInsight:too-short");
const sourceIds = new Set((answer.sources ?? []).map((source) => source.id));
for (const claim of answer.claims ?? []) {
  if (claim.kind === "original-framework") continue;
  if (!Array.isArray(claim.sourceIds) || claim.sourceIds.length === 0) failures.push(`claim:unsupported:${claim.text ?? "unknown"}`);
  for (const id of claim.sourceIds ?? []) if (!sourceIds.has(id)) failures.push(`claim:unknown-source:${id}`);
}
const result = { ok: failures.length === 0, failures, file };
process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
if (failures.length) process.exit(1);

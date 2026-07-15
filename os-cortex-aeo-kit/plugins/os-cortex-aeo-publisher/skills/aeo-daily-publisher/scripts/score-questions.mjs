#!/usr/bin/env node
import fs from "node:fs";

const file = process.argv[2];
if (!file) throw new Error("Usage: score-questions.mjs <questions.jsonl>");

const rows = fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean).map((line, index) => {
  try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON on line ${index + 1}`); }
});

const weights = { demand: .25, businessValue: .25, citationGap: .20, evidence: .20, freshness: .10 };
const eligible = rows.filter((row) => row.status === "queued" && row.evidence >= 60).map((row) => ({
  ...row,
  score: Math.round(Object.entries(weights).reduce((sum, [key, weight]) => sum + Number(row[key] ?? 0) * weight, 0) * 100) / 100,
})).sort((a, b) => b.score - a.score || a.question.localeCompare(b.question));

process.stdout.write(`${JSON.stringify({ selected: eligible[0] ?? null, candidates: eligible }, null, 2)}\n`);

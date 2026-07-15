#!/usr/bin/env node
import fs from "node:fs";
const file = process.argv[2]; if (!file) throw new Error("Usage: validate-brand-config.mjs <brand.yaml>");
const text = fs.readFileSync(file, "utf8"); const failures = [];
for (const key of ["brand:","organization:","canonical_domain:","audience:","offer:","approved_claims:","prohibited_claims:","experts:","cta:","tone:","source_of_truth_urls:"]) if (!text.includes(key)) failures.push(`missing:${key.slice(0,-1)}`);
if (/REPLACE_ME|example\.com|your brand/i.test(text)) failures.push("placeholder-values");
if (!/canonical_domain:\s*https:\/\//.test(text)) failures.push("canonical-domain:https-required");
const out = { ok: failures.length === 0, file, failures }; process.stdout.write(`${JSON.stringify(out,null,2)}\n`); if (failures.length) process.exit(1);

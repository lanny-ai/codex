#!/usr/bin/env node
import fs from "node:fs"; import path from "node:path";
const root = path.resolve(process.argv[2] ?? "."); const failures=[];
for (const rel of [".git",".openai/hosting.json","content/brand.yaml","content/questions.jsonl","content/runs","scripts"]) if (!fs.existsSync(path.join(root,rel))) failures.push(`missing:${rel}`);
const hostingPath=path.join(root,".openai/hosting.json"); if(fs.existsSync(hostingPath)){const h=JSON.parse(fs.readFileSync(hostingPath,"utf8")); if(!h.project_id) failures.push("hosting:missing-project-id");}
for(const name of fs.existsSync(root)?fs.readdirSync(root):[]) if(/^\.env/.test(name)&&name!==".env.example") failures.push(`secret-file-review:${name}`);
const out={ok:failures.length===0,root,failures}; process.stdout.write(`${JSON.stringify(out,null,2)}\n`); if(failures.length) process.exit(1);

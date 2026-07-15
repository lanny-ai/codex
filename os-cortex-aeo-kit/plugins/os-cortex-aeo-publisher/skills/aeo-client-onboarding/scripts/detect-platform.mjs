#!/usr/bin/env node
import os from "node:os";
const platforms = { darwin: "macOS", win32: "Windows", linux: "Linux" };
const result = { platform: platforms[process.platform] ?? process.platform, architecture: process.arch, node: process.version, homeDirectory: os.homedir(), supported: ["darwin", "win32", "linux"].includes(process.platform) };
process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
if (!result.supported) process.exit(1);

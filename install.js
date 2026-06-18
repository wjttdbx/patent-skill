#!/usr/bin/env node

/**
 * postinstall 脚本 — 将 skill 文件复制到 Claude Code / Cursor 的 skills 目录。
 *
 * 全局安装: npm install -g @wjttdbx/patent-skill
 * 项目安装: npm install --save-dev @wjttdbx/patent-skill
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILL_NAME = 'patent-disclosure-skill';

// npm 全局安装时 MANPATH / prefix 相关环境变量可能未设，
// 但 process.cwd() 在 postinstall 中即为包目录本身。
const SRC_DIR = process.cwd();

const EXCLUDE_DIRS = new Set([
  'node_modules',
  '.git',
  '__pycache__',
  '.vscode',
  '.idea',
]);

const EXCLUDE_FILES = new Set([
  '.gitignore',
  '.npmignore',
  'package-lock.json',
]);

function getTargetDirs() {
  const home = os.homedir();
  const dirs = [];

  // Claude Code — 全局 + 常见项目级
  dirs.push(path.join(home, '.claude', 'skills', SKILL_NAME));

  // Cursor — 全局
  dirs.push(path.join(home, '.cursor', 'skills', SKILL_NAME));

  return dirs;
}

function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      if (EXCLUDE_DIRS.has(entry.name)) continue;
      copyDir(srcPath, destPath);
    } else if (entry.isFile()) {
      if (EXCLUDE_FILES.has(entry.name)) continue;
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// —— main ——
const targets = getTargetDirs();

console.log(`\n📦 安装 Claude Code Skill: ${SKILL_NAME}\n`);

for (const target of targets) {
  try {
    copyDir(SRC_DIR, target);
    console.log(`  ✅ ${target}`);
  } catch (err) {
    console.error(`  ❌ ${target}: ${err.message}`);
  }
}

console.log(`\n✨ ${SKILL_NAME} 安装完成！在 Claude Code 中输入 /patent-disclosure-skill 即可使用。\n`);

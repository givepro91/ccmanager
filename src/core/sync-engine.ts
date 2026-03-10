import { readFile, writeFile, copyFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, basename } from "node:path";
import fg from "fast-glob";
import { CLAUDE_DIR, CLAUDE_MD, type CcmConfig } from "./config.js";

export interface SyncResult {
  project: string;
  files: { path: string; action: "created" | "updated" | "skipped" }[];
}

export async function syncToProject(
  hubDir: string,
  projectPath: string,
  config: CcmConfig,
): Promise<SyncResult> {
  const result: SyncResult = { project: projectPath, files: [] };

  // Sync shared rules
  if (config.shared.rules?.length) {
    const rulesDir = join(projectPath, CLAUDE_DIR, "rules");
    if (!existsSync(rulesDir)) {
      await mkdir(rulesDir, { recursive: true });
    }

    for (const rulePattern of config.shared.rules) {
      const rulePaths = await fg.glob(rulePattern, { cwd: hubDir, absolute: true });
      for (const rulePath of rulePaths) {
        const fileName = basename(rulePath);
        const targetPath = join(rulesDir, fileName);
        const action = existsSync(targetPath) ? "updated" : "created";
        await copyFile(rulePath, targetPath);
        result.files.push({ path: targetPath, action });
      }
    }
  }

  // Sync shared commands
  if (config.shared.commands?.length) {
    const commandsDir = join(projectPath, CLAUDE_DIR, "commands");
    if (!existsSync(commandsDir)) {
      await mkdir(commandsDir, { recursive: true });
    }

    for (const cmdPattern of config.shared.commands) {
      const cmdPaths = await fg.glob(cmdPattern, { cwd: hubDir, absolute: true });
      for (const cmdPath of cmdPaths) {
        const fileName = basename(cmdPath);
        const targetPath = join(commandsDir, fileName);
        const action = existsSync(targetPath) ? "updated" : "created";
        await copyFile(cmdPath, targetPath);
        result.files.push({ path: targetPath, action });
      }
    }
  }

  return result;
}

export async function collectFromProject(
  projectPath: string,
): Promise<{ claudeMd: boolean; rules: string[]; commands: string[]; hooks: boolean }> {
  const claudeMdPath = join(projectPath, CLAUDE_MD);
  const rulesDir = join(projectPath, CLAUDE_DIR, "rules");
  const commandsDir = join(projectPath, CLAUDE_DIR, "commands");
  const settingsPath = join(projectPath, CLAUDE_DIR, "settings.json");

  const rules = existsSync(rulesDir)
    ? await fg.glob("**/*", { cwd: rulesDir })
    : [];
  const commands = existsSync(commandsDir)
    ? await fg.glob("**/*", { cwd: commandsDir })
    : [];

  return {
    claudeMd: existsSync(claudeMdPath),
    rules,
    commands,
    hooks: existsSync(settingsPath),
  };
}

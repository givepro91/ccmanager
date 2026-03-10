import { Command } from "commander";
import { resolve } from "node:path";
import chalk from "chalk";
import { loadConfig, saveConfig } from "../core/config.js";
import { collectFromProject } from "../core/sync-engine.js";

export const addCommand = new Command("add")
  .description("Register a project to be managed by ccm")
  .argument("<path>", "Path to the project directory")
  .option("-a, --alias <name>", "Short alias for the project")
  .action(async (path: string, opts: { alias?: string }) => {
    const projectPath = resolve(path);
    const config = await loadConfig();

    if (config.projects.some((p) => p.path === projectPath)) {
      console.log(chalk.yellow("⚠") + ` Project already registered: ${projectPath}`);
      return;
    }

    const info = await collectFromProject(projectPath);
    config.projects.push({
      path: projectPath,
      alias: opts.alias,
    });

    await saveConfig(config);

    console.log(chalk.green("✓") + ` Added ${chalk.bold(opts.alias || projectPath)}`);
    console.log(
      `  CLAUDE.md: ${info.claudeMd ? "✓" : "✗"}  Rules: ${info.rules.length}  Commands: ${info.commands.length}  Hooks: ${info.hooks ? "✓" : "✗"}`,
    );
  });

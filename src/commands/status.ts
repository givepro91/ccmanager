import { Command } from "commander";
import chalk from "chalk";
import { loadConfig, getHubDir } from "../core/config.js";
import { collectFromProject } from "../core/sync-engine.js";

export const statusCommand = new Command("status")
  .description("Show all managed projects and their config status")
  .action(async () => {
    const config = await loadConfig();
    const hubDir = getHubDir();

    console.log(chalk.bold("ccm hub:") + ` ${hubDir}`);
    console.log(chalk.bold("Projects:") + ` ${config.projects.length}`);
    console.log();

    if (!config.projects.length) {
      console.log(chalk.dim("  No projects registered. Run `ccm add <path>` first."));
      return;
    }

    for (const project of config.projects) {
      const info = await collectFromProject(project.path);
      const label = project.alias
        ? `${chalk.cyan(project.alias)} ${chalk.dim(project.path)}`
        : project.path;

      console.log(`  ${label}`);
      console.log(
        `    CLAUDE.md: ${info.claudeMd ? chalk.green("✓") : chalk.red("✗")}  Rules: ${info.rules.length}  Commands: ${info.commands.length}  Hooks: ${info.hooks ? chalk.green("✓") : chalk.red("✗")}`,
      );
    }
  });

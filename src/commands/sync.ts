import { Command } from "commander";
import chalk from "chalk";
import { loadConfig, getHubDir } from "../core/config.js";
import { syncToProject } from "../core/sync-engine.js";

export const syncCommand = new Command("sync")
  .description("Sync shared configs to all registered projects")
  .option("-p, --project <alias>", "Sync only a specific project")
  .option("--dry-run", "Show what would be synced without making changes")
  .action(async (opts: { project?: string; dryRun?: boolean }) => {
    const config = await loadConfig();
    const hubDir = getHubDir();

    if (!config.projects.length) {
      console.log(chalk.yellow("No projects registered. Run `ccm add <path>` first."));
      return;
    }

    const targets = opts.project
      ? config.projects.filter((p) => p.alias === opts.project || p.path.includes(opts.project!))
      : config.projects;

    if (!targets.length) {
      console.log(chalk.red(`Project not found: ${opts.project}`));
      return;
    }

    for (const project of targets) {
      const result = await syncToProject(hubDir, project.path, config);
      const label = project.alias || project.path;

      if (result.files.length === 0) {
        console.log(chalk.dim(`  ${label}: no changes`));
      } else {
        console.log(chalk.green("✓") + ` ${chalk.bold(label)}`);
        for (const file of result.files) {
          const icon = file.action === "created" ? "+" : "~";
          const color = file.action === "created" ? chalk.green : chalk.yellow;
          console.log(`  ${color(icon)} ${file.path}`);
        }
      }
    }
  });

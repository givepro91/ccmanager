import { Command } from "commander";
import chalk from "chalk";
import { getHubDir, saveConfig, type CcmConfig } from "../core/config.js";

export const initCommand = new Command("init")
  .description("Initialize ccm hub directory for managing configs")
  .action(async () => {
    const hubDir = getHubDir();
    const config: CcmConfig = {
      version: "1",
      hub: hubDir,
      projects: [],
      shared: {
        rules: [],
        commands: [],
      },
    };

    await saveConfig(config);
    console.log(chalk.green("✓") + ` Initialized ccm hub at ${chalk.bold(hubDir)}`);
    console.log();
    console.log("Next steps:");
    console.log(`  ${chalk.cyan("ccm add")} <project-path>  Register a project`);
    console.log(`  ${chalk.cyan("ccm sync")}                Sync configs to all projects`);
    console.log(`  ${chalk.cyan("ccm status")}              Show all managed projects`);
  });

import { Command } from "commander";
import { initCommand } from "./commands/init.js";
import { syncCommand } from "./commands/sync.js";
import { statusCommand } from "./commands/status.js";
import { addCommand } from "./commands/add.js";

const program = new Command();

program
  .name("ccm")
  .description("Manage and sync Claude Code configurations across projects")
  .version("0.1.0");

program.addCommand(initCommand);
program.addCommand(syncCommand);
program.addCommand(statusCommand);
program.addCommand(addCommand);

program.parse();

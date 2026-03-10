import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import YAML from "yaml";

export const CCM_DIR = ".ccm";
export const CCM_CONFIG_FILE = "ccm.yaml";
export const CLAUDE_MD = "CLAUDE.md";
export const CLAUDE_DIR = ".claude";

export interface ProjectRef {
  path: string;
  alias?: string;
  lastSynced?: string;
}

export interface SharedConfig {
  rules?: string[];
  hooks?: Record<string, unknown>;
  commands?: string[];
  settings?: Record<string, unknown>;
}

export interface CcmConfig {
  version: string;
  hub: string;
  projects: ProjectRef[];
  shared: SharedConfig;
}

const DEFAULT_CONFIG: CcmConfig = {
  version: "1",
  hub: "",
  projects: [],
  shared: {
    rules: [],
    commands: [],
  },
};

export function getHubDir(): string {
  return resolve(process.env.CCM_HUB || join(process.env.HOME || "~", CCM_DIR));
}

export async function loadConfig(): Promise<CcmConfig> {
  const configPath = join(getHubDir(), CCM_CONFIG_FILE);
  if (!existsSync(configPath)) {
    return { ...DEFAULT_CONFIG, hub: getHubDir() };
  }
  const content = await readFile(configPath, "utf-8");
  return YAML.parse(content) as CcmConfig;
}

export async function saveConfig(config: CcmConfig): Promise<void> {
  const hubDir = getHubDir();
  if (!existsSync(hubDir)) {
    await mkdir(hubDir, { recursive: true });
  }
  const configPath = join(hubDir, CCM_CONFIG_FILE);
  await writeFile(configPath, YAML.stringify(config), "utf-8");
}

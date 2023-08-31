#!/usr/bin/env -S deno run --allow-env --allow-read --allow-write

import { walk } from "https://deno.land/std@0.200.0/fs/walk.ts";
import { basename, dirname } from "https://deno.land/std@0.200.0/path/mod.ts";

import { isEmpty } from "https://deno.land/x/lodash@4.17.15-es/lodash.js";

const home = Deno.env.get("HOME");
const backupDir = Deno.env.get("BACKUP_DIR") ?? `${home}/Downloads`;
const outputDir = `${backupDir}/processed-simple-tab-group-backup`;

type BackupFileContent = {
  groups: Array<{ tabs: Array<{ favIconUrl?: string }> }>;
};

class App {
  async run() {
    console.log(`Scanning for backup files: ${backupDir}`);

    const backupFilePaths = await this.getBackupFilePaths();

    if (isEmpty(backupFilePaths)) {
      console.error("Error: no backup files found");
      return;
    }

    await Promise.all(
      backupFilePaths.map((path) => this.processBackupFile(path)),
    );

    console.log("Backup files processed");
  }

  private async getBackupFilePaths(): Promise<Array<string>> {
    const backupFileWalker = walk(
      backupDir,
      {
        match: [/-backups-FF-/],
        includeDirs: false,
        exts: ["json"],
        maxDepth: 2,
      },
    );
    const result: Array<string> = [];

    for await (const { path } of backupFileWalker) {
      result.push(path);
    }

    return result;
  }

  private async processBackupFile(backupFilePath: string): Promise<void> {
    const backupDirName = basename(dirname(backupFilePath));
    const backupFileName = basename(backupFilePath);

    console.log(`- ${backupDirName}/${backupFileName}`);

    let fileContent: BackupFileContent;

    try {
      fileContent = JSON.parse(
        await Deno.readTextFile(backupFilePath),
      ) as BackupFileContent;
    } catch (e) {
      console.error("Error during processing", e);
      return;
    }

    for (const group of fileContent.groups) {
      for (const tab of group.tabs) {
        delete tab.favIconUrl;
      }
    }

    await this.writeProcessedBackupFile(
      backupFileName,
      backupDirName,
      fileContent,
    );
  }

  private async writeProcessedBackupFile(
    backupFileName: string,
    backupDirName: string,
    fileContent: BackupFileContent,
  ): Promise<void> {
    const outputFileDir = `${outputDir}/${backupDirName}`;

    await Deno.mkdir(outputFileDir, { recursive: true });

    const outputFilePath = `${outputFileDir}/${backupFileName}`;
    const fileData = JSON.stringify(fileContent, null, 2);

    await Deno.writeTextFile(outputFilePath, fileData);
  }
}

await new App().run();

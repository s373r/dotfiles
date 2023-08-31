#!/usr/bin/env -S deno run --allow-env --allow-read --allow-write

// A script to generate human-readable summary for the simple tab group Firefox extension backup files.
// This was needed to recover lost tabs.

import { walk } from "https://deno.land/std@0.200.0/fs/walk.ts";
import { basename, dirname } from "https://deno.land/std@0.200.0/path/mod.ts";

import { isEmpty } from "https://deno.land/x/lodash@4.17.15-es/lodash.js";

const home = Deno.env.get("HOME");
const backupDir = Deno.env.get("BACKUP_DIR") ?? `${home}/Downloads`;
const outputDir = `${backupDir}/processed-simple-tab-group-backup`;

type BackupFileContent = {
  groups: Array<{
    title: string;
    tabs: Array<{
      title: string;
      url: string;
      favIconUrl?: string;
    }>;
  }>;
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

    await this.writeProcessedBackupFileAndSummaryFile(
      backupFileName,
      backupDirName,
      fileContent,
    );
  }

  private async writeProcessedBackupFileAndSummaryFile(
    backupFileName: string,
    backupDirName: string,
    fileContent: BackupFileContent,
  ): Promise<void> {
    const outputFileDir = `${outputDir}/${backupDirName}`;

    await Deno.mkdir(outputFileDir, { recursive: true });

    const processedBackupFilePath = `${outputFileDir}/${backupFileName}`;
    const processedBackupFileData = JSON.stringify(fileContent, null, 2);

    await Deno.writeTextFile(processedBackupFilePath, processedBackupFileData);

    const summaryFilePath = `${outputFileDir}/summary-${backupFileName}`;
    const sortedFileContent = fileContent.groups.map((group) => ({
      title: group.title,
      tabs: group.tabs.map((tab) => ({ title: tab.title, url: tab.url })).sort((
        tab_left,
        tab_right,
      ) => tab_left.url.localeCompare(tab_right.url)),
    })).sort((group_left, group_right) =>
      group_left.title.localeCompare(group_right.title)
    );
    const summaryFileData = JSON.stringify(sortedFileContent, null, 2);

    await Deno.writeTextFile(summaryFilePath, summaryFileData);
  }
}

await new App().run();

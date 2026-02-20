#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

// Load environment variables
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../../.env.prod') });
dotenv.config(); 

const program = new Command();
const BACKEND_URL = process.env.R2R_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";
const LICENSE_KEY = process.env.SOVEREIGN_LICENSE_KEY || "";

const api = axios.create({
    baseURL: BACKEND_URL,
    headers: {
        'X-License-Key': LICENSE_KEY,
        'Content-Type': 'application/json'
    }
});

// --- PLATINUM BRANDING ---
const BANNER = `
  REALMS  2  RICHES
  SOVEREIGN INTELLIGENCE NETWORK
  v3.0.0-PLATINUM | SYSTEM: OPTIMAL
`;

function printBanner() {
    console.log(chalk.bold.hex('#00ff88')(BANNER));
    console.log(chalk.gray('  ' + '-'.repeat(40)));
}

program
  .name('r2r')
  .description('Realms 2 Riches - Platinum Sovereign Console')
  .version('3.0.0');

// --- UTILS ---
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function spinner(text, action) {
    const chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
    let i = 0;
    const loader = setInterval(() => {
        process.stdout.write(`\r${chalk.hex('#00ff88')(chars[i++ % chars.length])} ${text}`);
    }, 80);
    try {
        const res = await action();
        clearInterval(loader);
        process.stdout.write('\r'); 
        return res;
    } catch (e) {
        clearInterval(loader);
        process.stdout.write('\r');
        throw e;
    }
}

// --- CORE COMMANDS ---

program.command('status')
  .description('Display full system telemetry and health')
  .action(async () => {
    printBanner();
    console.log(chalk.blue('🔍 Scanning System Matrix...'));
    try {
      const res = await api.get(`/health`);
      const diag = await api.get(`/api/diagnostics`).catch(() => ({ data: {} }));
      
      console.log(chalk.white(`\nbackend:       `) + chalk.green('ONLINE') + chalk.gray(` (${BACKEND_URL})`));
      console.log(chalk.white(`swarm_state:   `) + (res.data.swarm === 'ACTIVE' ? chalk.green('ACTIVE') : chalk.yellow('RESTRICTED')));
      console.log(chalk.white(`agent_fleet:   `) + chalk.hex('#00ff88').bold(`${res.data.agents} Units`));
      console.log(chalk.white(`rag_memory:    `) + chalk.blue(`${res.data.rag} Vectors`));
      console.log(chalk.white(`db_connection: `) + (diag.data.db?.includes('connected') ? chalk.green('SECURE') : chalk.red('UNSTABLE')));
      console.log(chalk.white(`api_version:   `) + chalk.gray(res.data.version || 'Unknown'));
      
    } catch (error) {
      console.log(chalk.red('\n❌ CRITICAL FAILURE: Backend Unreachable'));
      console.log(chalk.gray(`Error: ${error.message}`));
    }
  });

program.command('task [description]')
  .description('Dispatch a directive to the Sovereign Swarm')
  .option('-f, --file <path>', 'Load task description from a file')
  .action(async (desc, options) => {
    let taskDesc = desc;
    if (options.file) {
        try { taskDesc = fs.readFileSync(options.file, 'utf-8'); }
        catch (e) { console.log(chalk.red(`❌ Error reading file: ${e.message}`)); return; }
    }
    if (!taskDesc) { console.log(chalk.yellow('⚠️  Please provide a task description or use -f <file>')); return; }

    console.log(chalk.blue(`\n🚀 Uplinking to Swarm Intelligence...`));
    try {
      const res = await spinner(chalk.yellow('Orchestrating Agents...'), async () => {
         return await api.post(`/api/tasks`, { description: taskDesc });
      });
      console.log(chalk.green('\n✅ Directive Executed Successfully.'));
      const result = res.data.result;
      if (result) {
          console.log(chalk.bold.hex('#00ff88')('\n╔══ SOVEREIGN REPORT ═════════════════════════════════'));
          console.log(chalk.white(result.reasoning || result.output || 'No output text generated.'));
          console.log(chalk.bold.hex('#00ff88')('╚═════════════════════════════════════════════════════\n'));
      }
    } catch (error) {
      console.log(chalk.red(`\n❌ Execution Failed: ${error.response?.data?.detail || error.message}`));
    }
  });

program.command('dev:autofix')
  .description('Self-healing code repair protocol')
  .action(async () => {
    console.log(chalk.magenta('🚑 Initiating Self-Healing Protocol...'));
    try {
      await spinner(chalk.blue('Running Diagnostics...'), async () => {
         execSync('npm test', { stdio: 'pipe' });
      });
      console.log(chalk.green('✅ System Integrity Verified. No repairs needed.'));
    } catch (testError) {
        console.log(chalk.yellow('\n⚠️  Fractures Detected. Deploying Repair Swarm...'));
        const errorLog = testError.stdout.toString() + testError.stderr.toString();
        try {
            const res = await api.post(`/api/tasks`, { description: `FIX ERROR: ${errorLog.substring(0, 500)}` });
            console.log(chalk.green('\n🛠️  Patch Applied Successfully.'));
            console.log(chalk.gray(res.data.result?.reasoning));
        } catch (e) {
            console.log(chalk.red(`❌ Repair Failed: ${e.message}`));
        }
    }
  });

// --- SHELL MODE ---
program.command('shell')
  .description('Enter the interactive Sovereign Command Console')
  .action(async () => {
      printBanner();
      const rl = (await import('readline')).createInterface({
          input: process.stdin,
          output: process.stdout,
          prompt: chalk.green('r2r> ')
      });
      rl.prompt();
      rl.on('line', async (line) => {
          const args = line.trim().split(' ');
          const cmd = args[0];
          const payload = args.slice(1).join(' ');
          if (!cmd) { rl.prompt(); return; }
          try {
              if (cmd === 'exit' || cmd === 'quit') process.exit(0);
              else if (cmd === 'status') {
                  const res = await api.get(`/health`);
                  console.log(chalk.green(`   System Online: ${res.data.agents} Agents | RAG: ${res.data.rag}`));
              } else if (cmd === 'task') {
                  await spinner(chalk.yellow('Executing...'), async () => {
                      const res = await api.post(`/api/tasks`, { description: payload });
                      console.log(chalk.green('\n✅ Done.'));
                      console.log(chalk.gray(res.data.result?.reasoning));
                  });
              } else console.log(chalk.red(`Unknown command: ${cmd}`));
          } catch (e) { console.log(chalk.red(`Error: ${e.message}`)); }
          rl.prompt();
      });
  });

program.parse();

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
const LICENSE_KEY = process.env.SOVEREIGN_LICENSE_KEY || "mock_dev_key";

const api = axios.create({
    baseURL: BACKEND_URL,
    headers: {
        'X-License-Key': LICENSE_KEY,
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
    }
});

// --- PLATINUM BRANDING ---
const BANNER = `
  REALMS  2  RICHES
  SOVEREIGN INTELLIGENCE NETWORK
  v3.9.5-PLATINUM | SYSTEM: OPTIMAL
`;

function printBanner() {
    console.log(chalk.bold.hex('#00ff88')(BANNER));
    console.log(chalk.gray('  ' + '-'.repeat(40)));
}

program
  .name('r2r')
  .description('Realms 2 Riches - Platinum Sovereign Console')
  .version('3.9.5');

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

// --- SHELL MODE (REALM REPL) ---

program.command('shell')
  .description('Enter the interactive Sovereign Command Console')
  .option('-y, --yolo', 'Enable YOLO mode (skip confirmations)', false)
  .action(async (options) => {
      printBanner();
      const rl = (await import('readline')).createInterface({
          input: process.stdin,
          output: process.stdout,
          prompt: chalk.green('r2r> ')
      });

      console.log(chalk.gray('Type "help" for commands. Type "exit" to quit.'));
      if (options.yolo) console.log(chalk.red.bold('⚠️  YOLO MODE ENGAGED: SAFETY CHECKS DISABLED'));

      rl.prompt();

      rl.on('line', async (line) => {
          const args = line.trim().split(' ');
          const cmd = args[0];
          const payload = args.slice(1).join(' ');

          if (!cmd) { rl.prompt(); return; }

          try {
              if (cmd === 'exit' || cmd === 'quit') {
                  process.exit(0);
              } else if (cmd === 'clear') {
                  console.clear();
                  printBanner();
              } else if (cmd === 'help') {
                  console.log(chalk.white(`
  Available Commands:
    task <desc>     - Submit a directive to the swarm
    status          - Check system health
    forecast        - View revenue projections
    learn <topic>   - Initiate a learning stream
    marketing       - Check marketing pulse
    exit            - Close session
                  `));
              } else if (cmd === 'status') {
                   const res = await api.get(`/health`);
                   console.log(chalk.green(`   System Online: ${res.data.agents} Agents | RAG: ${res.data.rag}`));
              } else if (cmd === 'task') {
                  if (!payload) { console.log(chalk.red('Error: Task description required.')); }
                  else {
                      await spinner(chalk.yellow('Orchestrating Agents...'), async () => {
                          const res = await api.post(`/api/tasks`, { description: payload });
                          console.log(chalk.green('\n✅ Task Complete.'));
                          console.log(chalk.gray(res.data.result?.reasoning || 'No output.'));
                      });
                  }
              } else if (cmd === 'learn') {
                  console.log(chalk.blue(`🌐 Initiating Learning Stream regarding: "${payload}"`));
                  await spinner(chalk.cyan('Scanning...'), async () => {
                      await api.post(`/api/tasks`, { description: `LEARN: Latest on ${payload}` });
                  });
                  console.log(chalk.green('✅ Knowledge Ingested.'));
              } else if (cmd === 'forecast') {
                  console.log(chalk.bold.white('📊 REVENUE PROJECTION (Est)'));
                  console.log(chalk.gray('   CONSERVATIVE: $2,900 MRR'));
                  console.log(chalk.blue('   MODERATE:     $29,000 MRR'));
                  console.log(chalk.green('   AGGRESSIVE:   $245,000 MRR'));
              } else {
                  console.log(chalk.red(`Unknown command: ${cmd}`));
              }
          } catch (e) {
              console.log(chalk.red(`Error: ${e.message}`));
          }
          
          rl.prompt();
      });
  });

program.parse();

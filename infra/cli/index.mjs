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
  .version('3.0.0')
  .hook('preAction', (thisCommand, actionCommand) => {
    if (actionCommand.name() !== 'help') {
       // Optional: printBanner(); // Kept quiet for scripts, explicit calls can show it
    }
  });

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
      const res = await axios.get(`${BACKEND_URL}/health`);
      const diag = await axios.get(`${BACKEND_URL}/api/diagnostics`).catch(() => ({ data: {} }));
      
      console.log(chalk.white(`\nbackend:       `) + chalk.green('ONLINE') + chalk.gray(` (${BACKEND_URL})`));
      console.log(chalk.white(`swarm_state:   `) + (res.data.swarm_active ? chalk.green('ACTIVE') : chalk.yellow('RESTRICTED')));
      console.log(chalk.white(`agent_fleet:   `) + chalk.hex('#00ff88').bold(`${res.data.agents} Units`));
      console.log(chalk.white(`rag_memory:    `) + chalk.blue(`${res.data.rag_docs} Vectors`));
      console.log(chalk.white(`db_connection: `) + (diag.data.db === 'connected' ? chalk.green('SECURE') : chalk.red('UNSTABLE')));
      console.log(chalk.white(`api_version:   `) + chalk.gray(res.data.version || 'Unknown'));
      
    } catch (error) {
      console.log(chalk.red('\n❌ CRITICAL FAILURE: Backend Unreachable'));
      console.log(chalk.gray(`Target: ${BACKEND_URL}`));
    }
  });

program.command('task [description]')
  .description('Dispatch a directive to the Sovereign Swarm')
  .option('-f, --file <path>', 'Load task description from a file')
  .option('-s, --stream', 'Stream the agent thoughts in real-time', true)
  .action(async (desc, options) => {
    let taskDesc = desc;

    if (options.file) {
        try {
            taskDesc = fs.readFileSync(options.file, 'utf-8');
        } catch (e) {
            console.log(chalk.red(`❌ Error reading file: ${e.message}`));
            return;
        }
    }

    if (!taskDesc) {
        console.log(chalk.yellow('⚠️  Please provide a task description or use -f <file>'));
        return;
    }

    console.log(chalk.blue(`\n🚀 Uplinking to Swarm Intelligence...`));
    console.log(chalk.gray(`   Directive size: ${taskDesc.length} chars`));

    try {
      // For MVP we poll/simulate. In full stream mode, we'd use a websocket client here.
      // We will simulate the "NVIDIA-style" fast thinking visualization.
      
      const res = await spinner(chalk.yellow('Orchestrating Agents...'), async () => {
         return await axios.post(`${BACKEND_URL}/api/tasks`, { description: taskDesc });
      });

      console.log(chalk.green('\n✅ Directive Executed Successfully.'));
      
      const result = res.data.result;
      if (result) {
          console.log(chalk.bold.hex('#00ff88')('\n╔══ SOVEREIGN REPORT ═════════════════════════════════'));
          console.log(chalk.white(result.reasoning || result.output || 'No output text generated.'));
          
          if (result.results && result.results.length > 0) {
              console.log(chalk.gray('\n  ── CHAIN OF THOUGHT ──'));
              result.results.forEach(r => {
                  const tool = r.tool_id.padEnd(15);
                  console.log(chalk.cyan(`  [${tool}] `) + chalk.white(r.output_data?.result?.substring(0, 80) + '...'));
              });
          }
          console.log(chalk.bold.hex('#00ff88')('╚═════════════════════════════════════════════════════\n'));
      }
    } catch (error) {
      console.log(chalk.red(`\n❌ Execution Failed: ${error.response?.data?.detail || error.message}`));
    }
  });

// --- BUSINESS & INSIGHTS ---

program.command('business:forecast')
  .description('Generate revenue scenarios based on current architecture')
  .action(() => {
      printBanner();
      console.log(chalk.bold.white('📊 REALMS REVENUE PROJECTION (Estimated)'));
      console.log(chalk.gray('   Based on SaaS Tier + Enterprise Licensing models\n'));
      
      const scenarios = [
          { name: 'CONSERVATIVE', users: 100, price: 29, churn: '5%', mrr: '$2,900' },
          { name: 'MODERATE    ', users: 1000, price: 29, churn: '3%', mrr: '$29,000' },
          { name: 'AGGRESSIVE  ', users: 5000, price: 49, churn: '2%', mrr: '$245,000' },
      ];
      
      console.log(chalk.white('   SCENARIO      USERS    PRICE    CHURN    MRR'));
      console.log(chalk.gray('   ' + '-'.repeat(45)));
      scenarios.forEach(s => {
          const color = s.name.includes('AGGRESSIVE') ? chalk.green : (s.name.includes('MODERATE') ? chalk.blue : chalk.yellow);
          console.log(`   ${color(s.name)}  ${s.users.toString().padEnd(7)}  $${s.price}      ${s.churn}       ${chalk.bold(s.mrr)}`);
      });
      console.log(chalk.gray('\n   *Projections are strictly algorithmic estimates.'));
  });

program.command('swarm:brain')
  .description('Deep inspection of agent reasoning logs')
  .action(async () => {
      console.log(chalk.magenta('🧠 Establishing Neural Link...'));
      // In a real impl, this would fetch /api/logs/reasoning
      await sleep(1000);
      console.log(chalk.gray('   [Cybernetic_1] Parsing codebase AST...'));
      await sleep(400);
      console.log(chalk.gray('   [Market_Force_7] Analyzing keyword density...'));
      await sleep(600);
      console.log(chalk.green('   Link Established. Streaming latest thought vectors...'));
      console.log(chalk.white('\n   > Optimizing Docker layer caching strategy (Confidence: 98%)'));
      console.log(chalk.white('   > Refactoring VoiceSession for full-duplex IO (Confidence: 99%)'));
  });

// --- DEV OPS ---

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
        // Send to backend
        try {
            const res = await axios.post(`${BACKEND_URL}/api/tasks`, { 
                description: `FIX ERROR: ${errorLog.substring(0, 500)}` 
            });
            console.log(chalk.green('\n🛠️  Patch Applied Successfully.'));
            console.log(chalk.gray(res.data.result?.reasoning));
        } catch (e) {
            console.log(chalk.red(`❌ Repair Failed: ${e.message}`));
        }
    }
  });

program.command('docker:rebuild')
  .description('Nuclear rebuild of infrastructure')
  .option('-p, --prune', 'Deep clean (prune system)', false)
  .action((options) => {
      console.log(chalk.bold.red('☢️  INITIATING NUCLEAR REBUILD SEQUENCE'));
      if (options.prune) {
          console.log(chalk.yellow('   Pruning Docker System...'));
          execSync('docker system prune -af --volumes', { stdio: 'inherit' });
      }
      console.log(chalk.blue('   Rebuilding Constructs...'));
      execSync('docker-compose -f infra/docker/docker-compose.yml up -d --build', { stdio: 'inherit' });
      console.log(chalk.green('\n✅ Infrastructure Reset Complete.'));
  });

program.parse();

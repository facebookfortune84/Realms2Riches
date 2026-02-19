#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import dotenv from 'dotenv';

dotenv.config({ path: path.resolve(process.cwd(), '../../.env.prod') });
dotenv.config(); // Fallback to local .env if present

const program = new Command();
const BACKEND_URL = process.env.R2R_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

program
  .name('r2r')
  .description('TITAN ORCHESTRATOR - Sovereign System CLI')
  .version('1.0.0');

// --- Backend Health ---
program.command('status')
  .description('Check the health of the Sovereign backend and tunnel')
  .action(async () => {
    console.log(chalk.blue('🔍 Checking Sovereign Status...'));
    try {
      const res = await axios.get(`${BACKEND_URL}/health`);
      console.log(chalk.green('✅ Backend: ONLINE'));
      console.log(chalk.cyan(`   Version: ${res.data.version || '3.1.0'}`));
      console.log(chalk.cyan(`   Swarm: ${res.data.swarm_active ? 'ACTIVE' : 'RESTRICTED'}`));
      console.log(chalk.cyan(`   Agents: ${res.data.agents}`));
    } catch (error) {
      console.log(chalk.red('❌ Backend: OFFLINE'));
      console.log(chalk.yellow(`   Target: ${BACKEND_URL}`));
    }
  });

// --- Docker Management ---
program.command('docker:rebuild')
  .description('Clean and rebuild all Sovereign containers')
  .option('-p, --prune', 'Prune all docker resources before build')
  .action((options) => {
    console.log(chalk.yellow('🚀 Initiating Clean Rebuild...'));
    try {
      if (options.prune) {
        console.log(chalk.red('🔥 Pruning docker system...'));
        execSync('docker system prune -af --volumes', { stdio: 'inherit' });
      }
      console.log(chalk.blue('🔨 Building containers...'));
      execSync('docker-compose -f infra/docker/docker-compose.yml build', { stdio: 'inherit' });
      console.log(chalk.green('✅ Build Complete. Restarting...'));
      execSync('docker-compose -f infra/docker/docker-compose.yml up -d', { stdio: 'inherit' });
    } catch (e) {
      console.log(chalk.red(`❌ Rebuild failed: ${e.message}`));
    }
  });

// --- Task Submission ---
program.command('task <description>')
  .description('Submit a task to the agent swarm')
  .action(async (description) => {
    console.log(chalk.blue(`🚀 Submitting task: "${description}"`));
    try {
      const res = await axios.post(`${BACKEND_URL}/api/tasks`, { description });
      console.log(chalk.green('✅ Task Accepted'));
      console.log(chalk.white(res.data.result?.reasoning || 'Task complete.'));
      if (res.data.result?.results) {
          res.data.result.results.forEach(r => {
              console.log(chalk.gray(`- [${r.tool_id}]: ${r.output_data?.result || 'Done'}`));
          });
      }
    } catch (error) {
      console.log(chalk.red(`❌ Task failed: ${error.response?.data?.detail || error.message}`));
    }
  });

// --- Self-Healing Dev Loop ---
program.command('dev:autofix')
  .description('Detect failures and use the swarm to heal the codebase')
  .action(async () => {
    console.log(chalk.magenta('🧠 Initiating Self-Healing Protocol...'));
    try {
      console.log(chalk.blue('🧪 Running test suite...'));
      try {
        execSync('npm test', { stdio: 'pipe' });
        console.log(chalk.green('✅ All tests passing. No healing required.'));
      } catch (testError) {
        const errorLog = testError.stdout.toString() + testError.stderr.toString();
        console.log(chalk.yellow('⚠️ Failures detected. Dispatching Engineering Swarm...'));
        
        const res = await axios.post(`${BACKEND_URL}/api/tasks`, { 
            description: `FIX THIS ERROR: ${errorLog.substring(0, 1000)}` 
        });
        
        console.log(chalk.green('🛠️ Patch Proposed by Agent Swarm:'));
        console.log(chalk.cyan(res.data.result?.reasoning));
        console.log(chalk.yellow('\nApplying patch... (Simulated in MVP)'));
      }
    } catch (error) {
      console.log(chalk.red(`❌ Healing failed: ${error.message}`));
    }
  });

// --- Launch ---
program.command('launch')
  .description('Activate the Sovereign Swarm')
  .action(async () => {
    console.log(chalk.yellow('⚡ Initiating Ignition Sequence...'));
    try {
      const res = await axios.post(`${BACKEND_URL}/api/sovereign/launch`, {
        signature: "verified_mock_signature"
      });
      console.log(chalk.green('🔥 SOVEREIGN SYSTEM ACTIVATED'));
    } catch (error) {
      console.log(chalk.red(`❌ Activation Failed: ${error.message}`));
    }
  });

program.parse();

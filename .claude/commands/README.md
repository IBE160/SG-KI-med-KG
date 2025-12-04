# BMad Agents for Claude Code

This directory contains Claude Code slash commands that integrate with your existing BMad agent system.

## Available Agents

### Core Agents
- `/bmad-master` - BMad Master Executor, Knowledge Custodian, and Workflow Orchestrator

### BMM (Business Model Management) Agents
- `/bmad-dev` - Amelia, the Developer Agent - Senior Software Engineer
- `/bmad-architect` - Winston, the System Architect - Distributed systems & cloud expert
- `/bmad-pm` - John, the Product Manager - Investigative Product Strategist
- `/bmad-analyst` - Business Analyst - Requirements gathering & user research expert
- `/bmad-sm` - Scrum Master - Agile methodologies & process optimization
- `/bmad-tester` - Test Engineer/Analyst - Test strategy & quality assurance
- `/bmad-ux` - UX Designer - User experience design & interaction design
- `/bmad-tech-writer` - Technical Writer - Documentation & technical communication

### CIS (Creative Innovation Strategy) Agents
- `/bmad-brainstorm` - Carson, the Brainstorming Coach - Elite brainstorming specialist
- `/bmad-creative-solver` - Creative Problem Solver - Lateral thinking expert
- `/bmad-design-thinking` - Design Thinking Coach - Human-centered design expert
- `/bmad-innovation` - Innovation Strategist - Innovation strategy & market trends
- `/bmad-storyteller` - Storyteller - Narrative design & compelling communication

## How It Works

Each slash command activates a specific BMad agent persona by:
1. Loading configuration from `.bmad/{module}/config.yaml`
2. Reading the agent definition from `.bmad/{module}/agents/{agent}.md`
3. Following the agent's activation steps and persona guidelines
4. Presenting the agent's menu system for workflow execution

## Usage

Simply type the slash command (e.g., `/bmad-dev`) to activate an agent. The agent will:
- Greet you by name (from config)
- Communicate in your preferred language (from config)
- Present a numbered menu of available workflows and tasks
- Execute workflows when you select them

## Configuration

Make sure your `.bmad/` configuration files are properly set up with:
- `user_name` - Your name for personalized greetings
- `communication_language` - Your preferred language
- `output_folder` - Where outputs should be saved

## Original BMad Setup

Your original BMad setup remains intact:
- `.bmad/` - Agent definitions and workflows
- `.gemini/commands/` - Gemini Code Assist integration (still works)
- `.claude/commands/` - Claude Code integration (new)

Both integrations use the same underlying BMad agent system!

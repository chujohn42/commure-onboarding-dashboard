# Commure Onboarding Intelligence Dashboard

## About

The Commure Onboarding Intelligence Dashboard is an ops command center for healthcare SaaS client launches. It gives onboarding teams real-time visibility into every client's progress through the launch pipeline, surfaces at-risk and blocked accounts before they slip, and uses Claude to automate the analytical and communication work — risk reasoning, blocker triage, RCM readiness checklists, and weekly executive briefs — that would otherwise eat up an onboarding manager's day.

## Modules

- **Onboarding Tracker** — a live, color-coded view of every client's milestone progress with AI-generated risk analysis and recommended interventions for at-risk and blocked accounts.
- **Blocker Triage** — submit a blocker description and get back a structured classification (type, severity, owner) plus resolution steps and a ready-to-send stakeholder message.
- **Metrics Engine** — throughput, defect rate, time-to-launch, and at-risk rate visualized with Plotly, plus an AI-generated weekly ops brief for VP-level reporting.
- **RCM Checklist** — describe a client's tech stack and get a categorized, priority-ranked revenue cycle management onboarding checklist.

## Tech Stack

- [Streamlit](https://streamlit.io/) for the application UI
- [Anthropic Claude](https://www.anthropic.com/) (claude-sonnet-4-6) for AI-driven analysis and generation
- [pandas](https://pandas.pydata.org/) for data handling
- [Plotly](https://plotly.com/python/) for visualizations

## Setup Instructions

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure your Anthropic API key in Streamlit secrets. Create `.streamlit/secrets.toml`:

   ```toml
   ANTHROPIC_API_KEY = "your-api-key-here"
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

## Live Demo

_Coming soon — placeholder for deployed app URL._

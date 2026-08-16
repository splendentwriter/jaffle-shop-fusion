# Jaffle Shop Reporting (Evidence.dev)

A single-page business overview report — revenue, the checkout/payment
funnel, top products, and fulfillment/shipping performance — built against
the `jaffle_shop_analytics` BigQuery dataset with [Evidence](https://evidence.dev).

## Setup

1. Node.js >= 18 (this project was set up with `nvm install --lts`).
2. Auth: connects via Application Default Credentials, scoped to a
   dedicated `evidence-reporting@jaffle-shop-505616.iam.gserviceaccount.com`
   service account (`bigquery.dataViewer` + `bigquery.jobUser` only — no
   write access). Point `GOOGLE_APPLICATION_CREDENTIALS` at that key
   (already set in `.env`, which is gitignored and never committed):
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/home/chibesa/.dbt/evidence-sa.json
   ```
   `.env` isn't auto-loaded by the `sources` CLI step — export it in your
   shell too if you hit "Could not load the default credentials":
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/home/chibesa/.dbt/evidence-sa.json
   ```

## Commands

```bash
npm install
npm run sources   # runs the real BigQuery queries (sources/jaffle_shop/*.sql), caches results locally
npm run dev       # local dev server with hot reload
npm run build     # static production build -> ./build
npm run preview   # serve the production build locally
```

## How queries work here

Real BigQuery SQL lives in `sources/jaffle_shop/*.sql` — that's what
actually runs against the warehouse during `npm run sources`, and the
results get cached locally. `pages/index.md`'s inline ```sql``` blocks are
thin pass-throughs (`select * from jaffle_shop.<queryname>`) that read that
local cache — they can't contain BigQuery-dialect SQL directly (backtick
identifiers, etc.), since page queries run against the local cache engine,
not BigQuery itself. Add a new metric by adding a `.sql` file under
`sources/jaffle_shop/`, then referencing it the same way in a page.

---

<details>
<summary>Original Evidence template README</summary>

# Evidence Template Project

## Using Codespaces

If you are using this template in Codespaces, click the `Start Evidence` button in the bottom status bar. This will install dependencies and open a preview of your project in your browser - you should get a popup prompting you to open in browser.

Or you can use the following commands to get started:

```bash
npm install
npm run sources
npm run dev -- --host 0.0.0.0
```

See [the CLI docs](https://docs.evidence.dev/cli/) for more command information.

**Note:** Codespaces is much faster on the Desktop app. After the Codespace has booted, select the hamburger menu → Open in VS Code Desktop.

## Get Started from VS Code

The easiest way to get started is using the [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Evidence.evidence-vscode):

1. Install the extension from the VS Code Marketplace
2. Open the Command Palette (Ctrl/Cmd + Shift + P) and enter `Evidence: New Evidence Project`
3. Click `Start Evidence` in the bottom status bar

## Get Started using the CLI

```bash
npx degit evidence-dev/template my-project
cd my-project
npm install
npm run sources
npm run dev
```

Check out the docs for [alternative install methods](https://docs.evidence.dev/getting-started/install-evidence) including Docker, Github Codespaces, and alongside dbt.

## Learning More

- [Docs](https://docs.evidence.dev/)
- [Github](https://github.com/evidence-dev/evidence)
- [Slack Community](https://slack.evidence.dev/)
- [Evidence Home Page](https://www.evidence.dev)

</details>

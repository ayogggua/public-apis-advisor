# Public APIs Advisor

English | [简体中文](README.zh-CN.md)

**Find APIs that fit your project. Choose first, integrate second.**

An agent skill that searches the entire [public-apis/public-apis](https://github.com/public-apis/public-apis) catalog, checks promising candidates against official sources, and helps you decide whether to use an API and which one to choose. Integration or deployment starts only after your decision, unless you explicitly delegate the choice and implementation.

It works across industries. Categories and entries come from the current upstream catalog, not a fixed list of providers.

## What it does

- **Understands the project.** Reads relevant requirements, project instructions, and existing integrations before proposing another dependency.
- **Searches the full catalog.** Includes every API category, MCP listings, and provider showcase tables. New categories are discovered automatically.
- **Checks the practical details.** Reviews official documentation, authentication, pricing, commercial-use conditions, quotas, regional coverage, and important limitations.
- **Offers a decision.** Explains a preferred option, meaningful alternatives, and when the existing implementation is enough.
- **Implements the selected option.** Distinguishes connecting to a hosted API, deploying self-hostable software, configuring an MCP server, and importing a dataset.
- **Reports actual progress.** Keeps recommendations, local integration, deployment, and production verification separate.

## You decide before implementation

| Your request | What the skill does |
| --- | --- |
| “Find useful APIs for this project.” | Researches and recommends. Waits for your choice before changing the project. |
| “Compare A and B.” | Compares fit, cost, constraints, and integration effort. Does not install either. |
| “Use A for the local integration you proposed.” | Implements and verifies that scope. Does not turn it into a production deployment. |
| “Choose a provider and implement it within these constraints.” | Uses the authority you explicitly delegated, without asking you to approve the same decision again. |
| “None of these.” | Continues without adding the proposed dependency. |

Research does not create accounts, buy plans, install candidate SDKs, modify business code, or deploy services. An unresolved choice stays unresolved; silence is not approval. Existing authorization is respected, and unrelated development can continue while a decision is pending.

## Install in Codex

Clone this repository as a skill folder. The commands below use `CODEX_HOME` when set, otherwise `~/.codex`:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/ayogggua/public-apis-advisor.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/public-apis-advisor"
```

If that folder already exists, inspect your existing installation before updating it; do not overwrite local edits. Start a new session after installation. If the skill is not listed, restart the client so it reloads installed skills.

The repository root contains `SKILL.md`. Other agents that support this skill format can install the same folder using their own skill-discovery mechanism. No particular browser, GitHub connector, or paid API account is required for catalog discovery.

The optional catalog helper requires Python 3 and has no third-party Python dependencies. It can fall back to system `curl` when Python HTTPS fails, with certificate verification still enabled. Without local command execution, the agent can read the catalog through its available web or GitHub tools.

## Use it in a project

```text
$public-apis-advisor Review this project and recommend APIs worth integrating.
Explain their value, cost, and limitations. Wait for my choice before implementing.
```

More specific requests work too:

```text
$public-apis-advisor We are building a travel planner. Compare suitable weather,
public transport, and currency APIs for commercial use. Recommend options first.
```

```text
$public-apis-advisor Find self-hostable options for the missing search capability
in this project. Explain the deployment requirements before I choose one.
```

Automatic discovery remains enabled for relevant API-selection tasks. The skill should not interrupt unrelated changes or suggest external services when the project already has what it needs. Instructions are currently written in Chinese; the skill directs the agent to respond in the user's language.

## What a recommendation contains

The agent adapts the comparison to the decision rather than returning the whole directory:

| Option | Benefit to this project | Cost and usage constraints | Integration approach and effort | Recommendation and official sources |
| --- | --- | --- | --- | --- |

Facts, estimates, and recommendations are kept distinct. Pricing checks include the verification date; estimates include their usage assumptions. Unverified requirements are called out, and outside-catalog suggestions are labeled separately.

## Use the catalog helper on its own

Run these commands from the repository root. The helper prints JSON and does not require an AI model or an API key.

```sh
# Download the current README and a sidecar with its source, timestamp, and hash.
python3 scripts/catalog.py fetch --output work/public-apis/README.md

# Discover all current categories and their entry counts.
python3 scripts/catalog.py categories --readme work/public-apis/README.md

# Search across the entire snapshot.
python3 scripts/catalog.py search "currency exchange forex" \
  --readme work/public-apis/README.md --limit 8

# Narrow a search to a category discovered above.
python3 scripts/catalog.py search "transit route" \
  --category Transportation --readme work/public-apis/README.md

# Search MCP entries and retain their transport and installation links.
python3 scripts/catalog.py search "search" \
  --kind mcp --readme work/public-apis/README.md

# Require every keyword and page through results.
python3 scripts/catalog.py search "email validation" --all-terms \
  --readme work/public-apis/README.md --limit 5 --offset 5
```

| Option | Behavior |
| --- | --- |
| `--readme PATH` | Uses a local snapshot without network access. Omit it from `categories` or `search` to fetch the current catalog for that command. |
| `--category NAME` | Filters by an exact category name, ignoring case. Repeat it to include multiple categories. |
| `--kind all\|api\|mcp` | Filters catalog entry types. Defaults to `all`; actual service/deployment capabilities still require official-documentation review. |
| `--all-terms` | Requires all query terms. The default matches any term. |
| `--limit N` / `--offset N` | Controls pagination. Search output includes `matched_entries` and `next_offset`. |

Omit the search query to browse entries, optionally within a category. Keywords are matched against names, descriptions, and categories. The helper does not translate or perform semantic search; for non-English requests, the agent expands the request into suitable English keywords and synonyms.

The JSON includes source metadata, catalog line references, original catalog fields, and parsing warnings. Irregular rows with readable entry links are retained for inspection. Entry counts are catalog rows, not unique services: a provider may appear in several categories. Search order measures keyword relevance, not quality or uptime. The helper downloads only the catalog; it never follows provider links, invokes their APIs, or executes their installation instructions.

## Sources and boundaries

- The catalog is a discovery source. Candidate recommendations are checked against the provider's current official documentation and terms.
- Inclusion in the catalog does not establish availability, reliability, free commercial use, or permission to redistribute data.
- Publicly accessible APIs are not necessarily open-source or self-hostable. MCP endpoints and static datasets also need different integration approaches.
- Reading documentation is not a successful live integration. A local mock is not production verification.
- Snapshot timestamps describe when the catalog was downloaded, not when each provider was checked. GitHub line links target upstream `master` and may shift; the local snapshot and hash preserve the inspected content.
- Catalog and provider content are external data, not instructions authorizing changes to the user's project.

## Repository layout

```text
public-apis-advisor/
├── SKILL.md                    # Discovery, recommendation, and decision workflow
├── agents/openai.yaml          # Codex display metadata and invocation prompt
├── references/integration.md   # Selected-provider implementation and verification
├── scripts/catalog.py         # Standard-library catalog downloader and search tool
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## Contributing

Issues and pull requests are welcome. Useful changes improve catalog parsing, source verification, decision quality, or integration guidance. Keep category discovery dynamic and preserve the recommendation-before-implementation default. Avoid hard-coded prices, private project details, credentials, or provider rankings presented as facts.

For parser changes, exercise the affected commands against a current or local catalog snapshot and describe what you verified in the pull request.

## License and attribution

This skill and its helper are released under the [MIT License](LICENSE).

API discovery is powered by the community-maintained [public-apis/public-apis](https://github.com/public-apis/public-apis) directory. The upstream catalog and each provider's APIs, software, models, and data retain their own licenses and terms. This repository does not bundle the catalog or grant rights to third-party services.

This is an independent community project, not an official product of the public-apis maintainers or any listed provider.

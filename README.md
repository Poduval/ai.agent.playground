# AI.Agent.Playground

**A practical playground for exploring AI concepts, technologies, frameworks, patterns, and implementations through focused examples and experiments.**

This repository is a learning playground, experimentation environment, and practical reference for AI capabilities and development patterns. Each major AI concept, technology, framework, or capability lives in its own top-level folder.

## Repository Structure

Each top-level folder represents a major AI concept, technology, framework, capability, or experimentation area:

```text
agents/
evaluation/
llm/
mcp/
memory/
microsoft-agent-framework/
multi-agent/
rag/
tool-calling/
workflows/
```

Supporting folders:

```text
shared/   # Reusable components across concepts (use sparingly)
docs/     # Repository-level documentation
```

Organization is **concept-first**, not provider-first. LLM providers are implementation choices within examples, not the primary structure.

## Examples

Each concept folder can contain multiple focused examples and experiments. For example:

```text
rag/
├── README.md
├── basic-rag/
├── hybrid-search/
└── reranking/
```

Examples should be small, focused, easy to understand, and independently runnable where practical.

## LLM Providers

This playground is designed to work with the LLM providers and models available to you. It is not tied to a single provider or gateway.

Examples may use providers such as:

- OpenAI
- Google Gemini
- xAI Grok
- NVIDIA
- Other OpenAI-compatible or cloud providers
- Local models when appropriate

Not every example supports every provider. Each example documents the providers, models, and credentials it needs.

## Design Principles

- Small and focused examples
- Easy to understand
- Independently runnable where practical
- Minimal unnecessary abstraction
- Concept-first organization
- Provider-agnostic where practical
- Provider-specific where useful
- Technology and framework flexibility
- Easy to extend
- Practical implementations over purely theoretical examples

## Adding a New Concept

Add a new top-level folder with a `README.md` and one or more focused examples:

```text
new-concept/
├── README.md
├── example-1/
└── example-2/
```

Do not create an `examples/` parent folder. New concepts should not require changes to existing ones.

## Adding an Example

1. Choose the concept folder that best matches what you are demonstrating.
2. Create a focused subfolder with a clear, hyphenated name.
3. Add a `README.md` covering what it demonstrates, setup, how to run, and required credentials.
4. Keep dependencies local to the example where practical.
5. Include a `.env.example` when API keys or environment variables are required.

## License

See [LICENSE](LICENSE).

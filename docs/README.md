# NLM System Documentation

## 📚 Documentation Index

### Core Documentation

- **[User Guide](user_guide.md)** - Comprehensive user guide covering all NLM system features, examples, and advanced usage patterns
- **[API Reference](api_reference.md)** - Complete API documentation for developers with class references, method signatures, and examples
- **[Multi-Agent Guide](multi_agent_guide.md)** - Multi-agent system architecture, agent types, and coordination patterns
- **[Prompt Standards](prompt_standards.md)** - Standard conventions for writing natural language macro prompts

### Additional Resources

- **[Test Overview](../tests/TEST_OVERVIEW.md)** - Test suite organization by priority for Claude Code sessions
- **[Archive](archive/)** - Archived documentation (edge case testing reports, etc.)

## Quick Navigation

### For New Users
1. Start with [User Guide](user_guide.md) for basic concepts and examples
2. Review [API Reference](api_reference.md) for detailed method documentation
3. Explore [Multi-Agent Guide](multi_agent_guide.md) for advanced workflows

### For Developers
1. [API Reference](api_reference.md) - Complete class and method documentation
2. [Test Overview](../tests/TEST_OVERVIEW.md) - Test priority and execution guidance
3. [Prompt Standards](prompt_standards.md) - Writing conventions for prompts

### For Claude Code Sessions
1. [Test Overview](../tests/TEST_OVERVIEW.md) - Critical tests to run first
2. [API Reference](api_reference.md) - Quick method lookup
3. [User Guide](user_guide.md) - Feature usage examples

## System Overview

The NLM (Natural Language Macro) system provides:
- **Natural Language Execution** with `{{variable}}` syntax
- **Session-based Variable Management** with namespace isolation
- **Global Variable Sharing** using `@prefix` syntax
- **Multi-Agent Coordination** for complex workflows
- **Multiple LLM Support** (OpenAI + Local models)

For complete setup and usage information, see the main [README.md](../README.md).
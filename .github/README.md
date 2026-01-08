# .github/ - GitHub Configuration

## Overview

This directory contains GitHub-specific configuration files for repository automation, CI/CD pipelines, and community standards.

## Structure

```
.github/
├── workflows/              # GitHub Actions CI/CD
│   ├── ci.yml             # Continuous Integration
│   └── cd.yml             # Continuous Deployment
├── ISSUE_TEMPLATE/        # Issue templates
│   ├── bug_report.md      # Bug report template
│   └── feature_request.md # Feature request template
├── CODEOWNERS             # Code ownership definitions
├── dependabot.yml         # Automated dependency updates
└── pull_request_template.md # PR template
```

## File Descriptions

### Workflows (`workflows/`)

#### `ci.yml` - Continuous Integration
Runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`

**Jobs:**
1. **Test** - Runs linting, type checking, and pytest
2. **Security** - Runs Bandit security scanner

#### `cd.yml` - Continuous Deployment
Handles automated deployment (configure based on your hosting).

### Templates

#### `ISSUE_TEMPLATE/bug_report.md`
Structured template for reporting bugs with:
- Bug description
- Steps to reproduce
- Expected vs actual behavior
- Environment details

#### `ISSUE_TEMPLATE/feature_request.md`
Template for requesting new features with:
- Problem description
- Proposed solution
- Alternative considerations

#### `pull_request_template.md`
PR template ensuring:
- Clear description of changes
- Testing checklist
- Documentation updates
- Breaking change notices

### Configuration Files

#### `CODEOWNERS`
Defines code ownership for automatic review requests. When a PR modifies certain files, the defined owners are automatically requested for review.

#### `dependabot.yml`
Configures automated dependency updates:
- Checks for outdated dependencies
- Creates PRs to update them
- Keeps project secure and up-to-date

## Customizing Workflows

### Adding Secrets
For CI/CD to work with external services, add secrets in:
`Settings → Secrets and variables → Actions`

Common secrets:
- `OPENAI_API_KEY` - For integration tests
- `CODECOV_TOKEN` - For coverage reporting

### Modifying CI Pipeline
Edit `workflows/ci.yml` to:
- Change Python version
- Add/remove linting tools
- Modify test commands
- Add deployment steps

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution workflow
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

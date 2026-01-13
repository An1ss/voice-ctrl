# Agent Preferences and Configuration

## Git/GitHub Preferences

### Authentication Method
**Preference:** SSH (Option 2)

When pushing to GitHub repositories:
- Use SSH authentication (git@github.com:...)
- Do NOT use HTTPS with tokens
- SSH keys are already configured and added to GitHub

**Commands:**
```bash
# Set remote to SSH
git remote set-url origin git@github.com:<username>/<repo>.git

# Push
git push -u origin <branch>
```

### GitHub Operations
- Remote URL format: `git@github.com:<username>/<repo>.git`
- SSH key already generated and added to GitHub account
- No need to prompt for authentication tokens

---

*This file documents user preferences for agent behavior.*

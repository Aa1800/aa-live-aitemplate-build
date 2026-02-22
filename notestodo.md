#TODO - Pre-Commit Hook (do later)
# Run: uv run ruff check . && uv run ruff format --check .
# Add to .git/hooks/pre-commit to block commits with lint errors

#TODO - Pre-Commit Hook (original notes)
Those 3 errors were introduced when I wrote main.py. There are two practical ways to prevent that:                                                                                              
  1. Pre-commit hook                                                                                        
  Run Ruff automatically before every commit so nothing with lint errors can be committed. Add this to      
  .git/hooks/pre-commit:                                                                                    
  uv run ruff check . && uv run ruff format --check .                                                       
  If Ruff fails, the commit is blocked. This is the safety net.

  2. Editor integration (real-time)
  The Ruff VS Code extension (or the built-in LSP via uv run ruff server) shows errors inline as you type —
  before you even save. This catches issues at the moment of writing, not after.

  For AI-generated code specifically, the most effective approach is the pre-commit hook — because the AI
  writes code and then you'd commit it. The hook forces a lint pass to happen in between, making it
  impossible to skip.

  The editor integration helps when you're writing, but the AI doesn't see your editor. The hook is the
  enforcement layer that catches both.

  Want me to set up the pre-commit hook?


#ToDo - Ruff Setup
Ruff did not add all instructions - refer to the github file later and see if we need anything else to be added, or if we need to update something on the process
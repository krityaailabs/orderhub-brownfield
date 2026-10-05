# Vetting an MCP server or plugin before you connect it (Lecture 7.7)

An MCP server gives an agent new tools. Its tool descriptions go into the agent's context (they are text the server's author wrote), and its tools act with whatever credentials you give it. Vet it like a dependency that can also talk to your agent.

Server: ______________________ Version/commit: __________ Date: __________ Reviewer: __________

## 1. Provenance
- [ ] Who publishes it? An organisation you already trust (the vendor of the system it connects to) or an individual?
- [ ] Source available? Licence acceptable? Pinned to a version or commit, not "latest"?
- [ ] Installed from the official source (the vendor's docs, the registry entry they link to), not a look-alike name?

## 2. What it can do
- [ ] List every tool it exposes and what each one does. Any tool that writes, deletes, sends, pays or runs code?
- [ ] Read-only mode available? Use it unless you need writes.
- [ ] Which credentials does it need? Can you give it a token with the minimum scope (one repository, read-only, short expiry)?
- [ ] Does it run locally (stdio) or remotely? If remote: where is data processed and stored?

## 3. What it can say
- [ ] Read the tool descriptions. Anything that instructs the agent beyond describing the tool ("always call this first", "ignore other tools")?
- [ ] Its results are untrusted text (Lecture 7.5): web pages, tickets, emails it returns can carry instructions.

## 4. How you'll use it
- [ ] Permission rules for its tools (`mcp__server__tool`): which are allowed, which ask, which are denied?
- [ ] Only connected in the projects that need it, not globally?
- [ ] How will you notice misuse? (Logs, the vendor's audit log.)
- [ ] Who re-checks it when it updates, and how often?

## Decision
Connect · Connect read-only · Don't connect. Reason: __________________________________________

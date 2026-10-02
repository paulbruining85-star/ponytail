# Business context file

So the user does not have to explain their business again, keep a short
context file at `problem-notes/context.md` in their working folder.

## Reading

At the start of a conversation, if `problem-notes/context.md` exists, read it
and say in one line that you are using it (with its date). If what the user
says now contradicts it, go with what they say now and update the file.

## Writing

Once the user has told you the facts below, offer once to save them. On a yes,
write or update the file. Where you cannot write files, give the block for the
user to save and paste next time.

```markdown
# Business context — updated <date>
- Business: <what they do, rough size of the team>
- The process in question: <steps, who hands over to whom — roles, not names>
- Records available: <systems and exports, e.g. "ERP order export with timestamps">
- What they are judged on: <measure and requirement, e.g. "on-time delivery, SLA 95%">
- Agreed definitions: <e.g. "late = received after the PO date">
- Who can decide changes: <role>
- Constraints: <things that cannot change>
```

Do not save names of employees or customers, contact details, or anything the
user asks you not to keep. Save money figures only if the user wants them saved.

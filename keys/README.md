# SSH public keys

Commit **your public key** here as `keys/<your-u-number>.pub` (for example
`keys/u123456.pub`).

We collect these from every portfolio, validate them, and submit them for you
to LIS-Unix so you get access to the GPU4EDU servers. Running
`python -m scripts.portfolio_check.check` validates yours as soon as you
commit it, so a mistake will be spotted here rather than as failing to `ssh` in
week 2.

> Curious why we're using these and how they work? See 
> [here](https://www.youtube.com/watch?v=GSIDS_lvRv4) (6 min).

## Generating a key

### First, open a terminal

A terminal is a window where you type commands instead of clicking. You will
live in one for the next seven weeks, so it is worth finding it properly now.

| | How to open one |
| --- | --- |
| **Windows** | Press the **Windows key**, type `powershell`, press Enter. A blue window opens. (**Git Bash** also works — it comes with Git; right-click in any folder → *Git Bash Here*.) |
| **macOS** | Press **⌘ + Space**, type `terminal`, press Enter. A white or black window opens. |
| **Linux** | **Ctrl + Alt + T** on most desktops, or search your applications for *Terminal*. |

You will see a line ending in `$`, `>` or `%` with a blinking cursor. That is
the prompt, and it is waiting for you. Type the command, press Enter.

> [!tip] Pasting commands into a terminal
> **Ctrl + V** does not always paste in a terminal. On Windows PowerShell use
> **right-click**. On macOS **⌘ + V** works normally. On Linux it is usually
> **Ctrl + Shift + V**.

### Then run this

```bash
ssh-keygen -t ed25519 -C "your.name@tilburguniversity.edu"
```

It will ask you three things. **You can press Enter for all three:**

1. *"Enter file in which to save the key"* — press Enter to accept the default.
   Do not type a name here; the rest of these instructions assume the default.
2. *"Enter passphrase"* — you may leave it empty, or set one. A passphrase
   protects the key if someone gets your laptop, and you will be asked for it
   each time you push. Either choice is fine; if you set one, do not forget it.
3. *"Enter same passphrase again"* — repeat it, or press Enter again.

Then it prints something like `The key fingerprint is: SHA256:...` and a box of
ASCII art. That means it worked. **Do not run the command a second time**; it
will offer to overwrite your key, and if you say yes, anything already using the
old one stops working.

> [!note] If `ssh-keygen` reports *"command not found"* or *"not recognized"*: try
> opening Git Bash and run exactly the same command there.

### Where did the files go?

Into a hidden folder called `.ssh` in your home directory. Hidden folders do not
show up in Explorer or Finder by default, which is why you should use the
terminal to look:

```bash
ls ~/.ssh
```

You should see `id_ed25519` and `id_ed25519.pub`.

To copy the **public** one into this folder, from the root of your project:

```bash
cp ~/.ssh/id_ed25519.pub keys/uXXXXXX.pub
```

Replace `uXXXXXX` with your own u-number. Then `git add`, `git commit`,
`git push`, and run `python -m scripts.portfolio_check.check`.

## Check, check, double check

`ssh-keygen` produces two files:

| File | What it is | What to do with it |
| --- | --- | --- |
| `id_ed25519.pub` | your **public** key | commit it here |
| `id_ed25519` | your **private** key | **⚠️ never share it, never commit it ‼️** |

The public key is meant to be public. That is the whole point of the design.
The private key is the secret. If you ever commit the private one by accident: 

- delete it, 
- generate a new pair, 
- tell us.

It's safest to rotate the key if credentials are leaked (treat it like a
password, because it is).

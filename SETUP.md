# Finish Assignment 6

The application files are ready. Complete these steps on your Windows computer.

## 1. Start Docker Desktop

Open Docker Desktop and wait until its engine is running. In PowerShell:

```powershell
docker info --format 'Docker server: {{.ServerVersion}} | Container OS: {{.OSType}}'
```

The container OS must be `linux`.

## 2. Prepare the local runtime environment

From the `ai-agent-actions` project folder:

```powershell
Copy-Item .env.example "$env:USERPROFILE\.ai-agent-actions.env"
notepad "$env:USERPROFILE\.ai-agent-actions.env"
```

Replace the API-key placeholder with your existing Gemini key. You can find it in the original AI Inventory-Agent project's `.env`. Replace the Django secret placeholder with a long random value. Keep this file local; do not upload it or paste its contents into chat. If this file already exists, edit it instead of copying over it.

The runner must run under this same Windows user, since deployment reads that user's profile folder.

## 3. Register the self-hosted runner

Open:
https://github.com/nabilnabhan61/ai-agent-actions/settings/actions/runners/new

Choose **Windows**, **x64**. Follow GitHub's current download, hash-verification, extraction, and configuration commands. Use a folder outside the project, for example:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\actions-runner-ai-agent"
Set-Location "$env:USERPROFILE\actions-runner-ai-agent"
```

Use the configuration command GitHub displays (its registration token expires). Answer:

- Runner group: default
- Runner name: `ai-agent-local`
- Additional label: **`ai-agent-deploy`**
- Work folder: default (`_work`)
- Run as service: **N**, matching the tutorial

Then start it:

```powershell
.\run.cmd
```

Keep that PowerShell window open. GitHub should show the runner as **Idle**. Keep Docker Desktop and the computer running throughout the lab. Use a separate PowerShell window for the next steps.

## 4. Push the prepared project

Open PowerShell in the `ai-agent-actions` folder, not the parent assignment folder.

The local repository is prepared with `main` and the correct `origin`. Run:

```powershell
git push -u origin main
```

Complete GitHub's sign-in prompt if shown. Do not use your account password as a Git password. If Git reports an authentication error, use Git Credential Manager's browser sign-in or GitHub Desktop to publish the existing local repository.

## 5. Check the first deployment

Open https://github.com/nabilnabhan61/ai-agent-actions/actions

The `test` job should pass, then the `deploy` job should pass. If deploy is queued, verify the runner is online with the exact `ai-agent-deploy` label. If it reports a missing environment file, finish step 2. If it cannot connect to Docker, finish step 1.

Open http://localhost:8000 and confirm the Inventory Agent appears.

Create an admin account in the persistent database:

```powershell
docker exec -it ai-agent-actions-app python manage.py createsuperuser
```

Open http://localhost:8000/admin/ and add an inventory item, then test the chat. A green deployment confirms HTTP startup, not Gemini credentials or model access; test a real inventory question separately.

## 6. Invite the instructor

Open https://github.com/nabilnabhan61/ai-agent-actions/settings/access

Click **Add people**, search for **am38@aub.edu.lb**, verify the matching account, and send the collaborator invitation. The assignment requires sending the invitation; acceptance depends on the instructor. If GitHub cannot find the email, ask the instructor for their GitHub username instead of guessing.

## 7. Demonstrate continuous deployment in the lab

1. Show the workflow file and the successful `test` and `deploy` jobs.
2. Show the running app and an existing inventory item.
3. Change the visible assignment line in `chat/templates/chat.html`, for example append ` - live update`.
4. Commit and push:

```powershell
git add chat/templates/chat.html
git commit -m "Demonstrate automatic deployment"
git push
```

5. Watch a new Actions run finish successfully.
6. Refresh http://localhost:8000 and show the new text without manually pulling or restarting Docker.
7. Show that the inventory item still exists after container replacement.
8. Show the instructor invitation in repository settings.

## Restart for a later lab session

Start Docker Desktop, then run `run.cmd` in your runner folder. The container has an `unless-stopped` restart policy. To redeploy the current code, open Actions, select **CI and local deployment**, then **Run workflow** on `main`.

## Useful diagnostics

```powershell
docker ps --filter name=ai-agent-actions-app
docker logs --tail 80 ai-agent-actions-app
docker inspect --format '{{.State.Health.Status}}' ai-agent-actions-app
```

If port 8000 is already occupied, identify the other app/container before stopping it. The deployment replaces only `ai-agent-actions-app`; it does not remove other projects or the persistent data volume.

## Completion checklist

- [ ] Code pushed to the new repository
- [ ] CI checks, image build, and smoke test green
- [ ] Image published to GHCR
- [ ] Windows runner online and deploy job green
- [ ] App and real Gemini chat work locally
- [ ] Visible edit redeploys automatically and inventory survives
- [ ] Instructor invitation sent
- [ ] Deployment demonstrated in the lab

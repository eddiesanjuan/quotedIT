# Deploying Quoted to Railway

This guide walks through deploying Quoted to Railway with PostgreSQL.

## Prerequisites

- [Railway account](https://railway.app)
- Railway CLI installed (`npm install -g @railway/cli`)
- Your API keys ready:
  - Anthropic API Key (for Claude)
  - OpenAI API Key (for Whisper transcription)

## Quick Deploy

### 1. Login to Railway

```bash
railway login
```

### 2. Initialize Project

```bash
cd quoted
railway init
```

Select "Create new project" when prompted.

### 3. Add PostgreSQL

```bash
railway add --database postgres
```

### 4. Set Environment Variables

```bash
# Required
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set OPENAI_API_KEY=sk-...

# Generate a secure JWT secret
railway variables set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Optional (defaults are fine)
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set TRANSCRIPTION_PROVIDER=openai
railway variables set CLAUDE_MODEL=claude-sonnet-4-20250514
```

Railway automatically sets `DATABASE_URL` for the PostgreSQL addon.

### 5. Deploy

```bash
railway up
```

### 6. Get Your URL

```bash
railway domain
```

This generates a public URL like `quoted-production.up.railway.app`.

## Post-Deployment

### Test the Deployment

1. Visit your Railway URL
2. Register a new account
3. Try generating a quote

### Custom Domain (Optional)

```bash
railway domain add yourdomain.com
```

Then configure your DNS to point to Railway.

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for quote generation |
| `OPENAI_API_KEY` | Yes | OpenAI key for Whisper transcription |
| `JWT_SECRET_KEY` | Yes | Secret for JWT token signing (generate random) |
| `DATABASE_URL` | Auto | PostgreSQL connection string (Railway sets this) |
| `ENVIRONMENT` | No | `development` or `production` |
| `DEBUG` | No | `true` or `false` |
| `TRANSCRIPTION_PROVIDER` | No | `openai` or `deepgram` |
| `CLAUDE_MODEL` | No | Claude model to use |

## Troubleshooting

### Database Issues

If you see database errors, ensure PostgreSQL is properly linked:

```bash
railway status
```

Should show both the web service and PostgreSQL.

### Build Failures

Check the build logs:

```bash
railway logs
```

Common issues:
- Missing dependencies: Check `requirements.txt`
- Python version: Ensure `nixpacks.toml` specifies Python 3.11

### API Key Issues

Verify your environment variables are set:

```bash
railway variables
```

## Monitoring

View logs in real-time:

```bash
railway logs --follow
```

## Scaling

Railway automatically handles scaling. For manual control:

```bash
railway scale web=2  # Run 2 instances
```

## Cost Estimate

- **Starter Plan**: Free tier includes $5/month
- **PostgreSQL**: ~$5-10/month for small usage
- **Compute**: Pay per usage, typically $5-20/month

Total: ~$10-30/month for a production deployment.

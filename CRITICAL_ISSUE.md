# 🚨 CRITICAL ISSUE: Events Keep Disappearing

## Problem

November and December events keep disappearing from GitHub after being correctly added to the system.

## Evidence

1. **Local file**: ✅ Has all 22 events (including Nov/Dec)
2. **GitHub**: ❌ Only has 11 events (October only)
3. **update_calendar_data.py**: ✅ Has all 22 events in code

## Timeline of Events

| Time | Event | Events Count |
|------|-------|--------------|
| 15:10 | Pushed 22 events (with AI extraction) | 22 ✅ |
| 15:39 | **Unknown push removed events** | 11 ❌ |
| 16:06 | Fixed and pushed 22 events | 22 ✅ |
| 16:45 | Pushed uniform sync update | 22 ✅ |
| 01:05 (Oct 7) | **Unknown push removed events again** | 11 ❌ |
| 08:19 (Oct 7) | Pushed 22 events again | 22 ✅ |
| Current | GitHub still showing 11 (CDN cache?) | 11 ❌ |

## Root Cause

There is an **external process** pushing updates with OLD data that only has October events. This process is running at unusual times (15:39, 01:05) which are NOT our scheduled times (06:00, 18:00).

### Possible Sources:

1. **Another server/computer** running the old version of update_calendar_data.py
2. **External application** modifying the GitHub data directly
3. **Webhook or automation** triggered by GitHub that runs old code
4. **Scheduled task on another system** (not this sandbox)
5. **GitHub Actions** or CI/CD pipeline running old code

## What's Being Lost

### November Events (3 events):
- Anti-Bullying Week Start (Nov 10)
- Odd Socks Day (Nov 10)
- Anti-Bullying Week End (Nov 14)

### December Events (2 events):
- Christmas Party (Dec 12)
- Last Day of Term (Dec 12)

## Verification

Run this command to check status:
```bash
cd /home/ubuntu/school-calendar-data
python3 verify_events.py
```

To automatically fix:
```bash
python3 verify_events.py --fix
```

## Immediate Actions Needed

### 1. Find the External Process ⚠️

**Check these locations:**
- Other computers/servers with access to the GitHub repository
- GitHub Actions workflows (`.github/workflows/`)
- External services with GitHub API access
- Scheduled tasks on other systems
- Any deployed applications that might update the calendar

### 2. Stop the External Process

Once found, either:
- Update it to use the new code with 22 events
- Disable it completely
- Ensure it pulls latest code before running

### 3. Verify GitHub Repository Settings

Check if there are:
- Branch protection rules
- Required status checks
- Automated workflows
- Webhooks configured

## Temporary Workaround

Until the external process is found and stopped:

1. **Monitor regularly**:
   ```bash
   python3 /home/ubuntu/school-calendar-data/verify_events.py
   ```

2. **Auto-fix when detected**:
   ```bash
   python3 /home/ubuntu/school-calendar-data/verify_events.py --fix
   ```

3. **Add to scheduled tasks** to run verification every hour

## Long-term Solution

1. **Find and stop** the external process
2. **Centralize updates** to only run from this system
3. **Add validation** to prevent pushes with < 22 events
4. **Enable branch protection** on GitHub to require review
5. **Add monitoring** to alert when events disappear

## Questions to Answer

1. ❓ Are there other computers/servers with this repository cloned?
2. ❓ Is there a GitHub Actions workflow configured?
3. ❓ Does the external application have write access to GitHub?
4. ❓ Are there any webhooks configured on the repository?
5. ❓ Is there a CI/CD pipeline running somewhere?

## Files to Check

- `.github/workflows/` - GitHub Actions
- `schedule_updates.sh` - Scheduled task configuration
- GitHub repository settings → Webhooks
- GitHub repository settings → Actions
- Any deployed application code that might update the calendar

---

**Status**: 🔴 **UNRESOLVED**  
**Impact**: High - Users missing November and December events  
**Priority**: Urgent - Needs immediate investigation  

**Last Updated**: October 7, 2025 at 08:21 AM

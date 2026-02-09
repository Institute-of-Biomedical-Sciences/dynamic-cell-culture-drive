# Updating Services

## Overview

This document describes the process for updating services by pulling the latest release from the GitHub repository. Updates are managed through Git tags and releases, ensuring consistency and traceability across deployments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Update Procedure](#update-procedure)
- [Notes](#notes)

## Prerequisites

Before updating, ensure that:
- Git is installed on the system
- You have access to the target repository
- The service repository has already been cloned locally

## Update Procedure

Follow the steps below to update the service to the latest available release.

### 1. Fetch Latest Changes and Tags

Retrieve the most recent commits and all release tags from the remote repository:

```bash
git fetch --tags
git pull
```

This updates the local repository with the latest changes from the default branch and makes new release tags available.

### 2. Check Out a Specific Release (Optional)

If you need to update to a specific released version, check out the corresponding tag:

```bash
git checkout v<version-number>
```
Replace `version-number` with the desired release version (for example, `v1.2.3`).

## Notes

- GitHub releases are based on tags; checking out a tag places the repository in a detached HEAD state.
- For automated deployments, consider scripting this process or pinning a specific release version.
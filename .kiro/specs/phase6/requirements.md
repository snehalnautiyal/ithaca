# Phase 6 Requirements — Deep Research

## REQ-1: Pipeline
- WHEN a user submits a research query, THEN run a multi-step pipeline:
  1. Decompose the question into 3-5 sub-queries.
  2. Search each sub-query via SearXNG.
  3. Fetch and extract content from top results.
  4. Synthesize a structured report with citations.

## REQ-2: Live progress
- Stream progress events to the UI: sub-queries generated, searches completed, sources fetched, synthesis started.

## REQ-3: Report output
- Output a Markdown report with headings, links, and a sources list.
- Save the report to the documents workspace automatically.

## REQ-4: Graceful fallback
- IF SearXNG is unavailable, THEN report the error and attempt synthesis from what the LLM already knows.

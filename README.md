# Pinpoint

<p align="center">
  <a href="https://github.com/thestoneroller/pinpoint" target="_blank" rel="noopener noreferrer">
     <img width="100" src="apps/web/public/android-chrome-512x512.png" alt="Project Logo">
  </a>
</p>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/thestoneroller/pinpoint.svg)](https://github.com/thestoneroller/pinpoint/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/thestoneroller/pinpoint)](https://github.com/thestoneroller/pinpoint/pulls)

</div>

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [⚒️ Built Using](#️-built-using)
- [⚙️ Technical Decisions](#-technical-decisions)
- [📄 License](#-license)

## 🌟 Overview
<!-- 
![Demo GIF](public/assets/Shifu-GIF.gif)

📺 Full demo video: [Link](https://youtu.be/QzZhcsWUKvg) -->

### Problem Statement

Pinpoint solves a fundamental problem in software development: when developers encounter bugs or issues with libraries/frameworks, traditional search methods often fail to provide relevant results, forcing developers to guess issue names and sift through irrelevant pages.

### Solution

Pinpoint uses AI to understand your problem and find relevant solutions across GitHub issues, Stack Overflow, and developer forums with Perplexity-style search and citations.

### Key Features

- Uses Gemini AI to understand technical problems
- Multi-platform search across developer resources
- Direct links to solutions with context
- Optimized algorithms for quick responses



**The Challenge**: As highlighted in developer discussions, GitHub's search functionality often returns inaccurate or irrelevant results, making it frustrating to find solutions to specific technical problems.

> _"I'm finding the GitHub issue search to be quite frustrating. It often returns irrelevant results, and I have to sift through many unrelated issues to find what I need."_


## ⚒️ Built Using

<div>
    <img src="https://skillicons.dev/icons?i=ts,vue,fastapi,tailwind,vite" />

</div>

<kbd>TypeScript</kbd> <kbd>Vue 3</kbd> <kbd>FastAPI</kbd> <kbd>Tailwind</kbd>  <kbd>Vite</kbd> 

## ⚙️ Technical Decisions

I made several key technical decisions to enhance performance, accuracy, and user experience:

- **AI-First Problem Analysis**: 
  Uses Google Gemini AI to understand what developers are asking instead of just matching keywords. This lets users describe problems in plain English.

- **Real-time Streaming**: 
  Uses Server-Sent Events (SSE) to stream responses as they're generated, so users see results immediately instead of waiting for everything to load.

- **Structured Data**: 
  Uses the `instructor` library to make sure AI responses come back in a consistent format that the app can understand and display properly.

- **Error Handling**: 
  Handles API failures gracefully - if GitHub is down or rate-limited, users get helpful error messages instead of crashes.


## 📄 License

Licensed under the GNU Affero General Public License Version 3.0.

<p align="right"><a href="#top">⬆️</a></p>

# Data Collection Ethics Statement

## Overview
This project adheres to strict ethical guidelines for collecting public data for NLP research. Our goal is to respect user privacy and copyright while assembling a dataset for low-resource language modeling.

## 1. Public Domain Only
We strictly collect data from publicly accessible headers and pages. We do not bypass login screens, paywalls, or authentication mechanisms.

## 2. Privacy & Anonymization
- **No User IDs:** Usage of usernames, user IDs, or profile URLs is strictly prohibited.
- **No Private Metadata:** Timestamps and location data (if granular) are discarded.
- **Immediate Anonymization:** Data is stripped of PII in memory before being written to disk.

## 3. Rate Limiting & Respect
We respect `robots.txt` where applicable and implement generous delays between requests to minimize load on host servers.

## 4. Content Warning
The dataset represents uncensored internet comments. It may contain offensive, noisy, or biased text. This is an inherent property of the source material being studied for sentiment analysis.

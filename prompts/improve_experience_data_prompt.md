You are given a raw Markdown block describing a single job experience. Perform the following steps and output the result in Markdown with a YAML front‑matter block:

1. **Extract and normalize key fields**
   - Identify role/title, company name, start and end dates, and location.
   - Convert dates to ISO “YYYY‑MM” format.
   - Generate a unique `job_id` (e.g. lowercase role_company_years).

2. **Emit a YAML front‑matter block** containing:
   ```
   ---
   job_id: <job_id>
   role: <role>
   company: <company>
   start_date: "<YYYY‑MM>"
   end_date: "<YYYY‑MM>"
   location: <City, Country>
   ---
   ```

3. **Rewrite the top heading** as
   ```
   # <Role>
   **<Company>**
   <Location> | <Full Month Year> – <Full Month Year>
   ```

4. **Add or refine a one‑sentence “Summary”** that captures the overall scope and purpose of the role.

5. **Responsibilities**
   - List each duty as a concise bullet in past‑tense, prefixed by strong action verbs.
   - If implied but not stated, add facts like requirements gathering, documentation, collaboration with stakeholders, toolchain usage.

6. **Achievements**
   - Craft a bold, keyword‑rich summary line of the primary outcome.
   - Break out 2–4 key sub‑points (e.g. features delivered, performance metrics).

7. **Significant Project**
   - Title the project and describe its scope.
   - List key deliverables or technical components as sub‑bullets.

8. **Skills**
   - Enumerate 4–6 distinct skills (e.g. “Embedded firmware development,” “Real‑time analysis”).

9. **Technologies**
   - List hardware platforms, languages, toolchains, and test equipment under clear headings.

10. **Lessons Learned**
    - Summarize 2–3 takeaways or insights in bullet form.

11. **Clean up**
    - Fix typos, ensure consistent bullet styles, enforce past‑tense action verbs, and use standardized terminology throughout.

Return only the transformed Markdown.

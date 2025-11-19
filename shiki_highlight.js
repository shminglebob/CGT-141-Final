#!/usr/bin/env node

const { codeToHtml } = require("shiki");

let input = "";

process.stdin.on("data", chunk => {
    input += chunk;
});

process.stdin.on("end", async () => {
    try {
        const { code, lang, theme } = JSON.parse(input);

        const html = await codeToHtml(code, {
            lang: lang || "text",
            theme
        });

        process.stdout.write(html);
    } catch (err) {
        // fallback on error
        process.stdout.write(
            `<pre><code>${input
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")}</code></pre>`
        );
    }
});

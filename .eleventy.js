const markdownIt = require("markdown-it");
const markdownItFootnote = require("markdown-it-footnote");
const markdownItAnchor = require("markdown-it-anchor");

module.exports = function(eleventyConfig) {

  // Markdown with footnotes + anchor links
  const md = markdownIt({ html: true, linkify: true, typographer: true })
    .use(markdownItFootnote)
    .use(markdownItAnchor);
  eleventyConfig.setLibrary("md", md);

  // Pass through static assets
  eleventyConfig.addPassthroughCopy("src/assets");

  // Pass through the PDF
  eleventyConfig.addPassthroughCopy({ "src/thesis/yellow-duck-thesis.pdf": "thesis/yellow-duck-thesis.pdf" });

  // Filters
  eleventyConfig.addFilter("year", () => new Date().getFullYear());

  eleventyConfig.addFilter("formatDate", (d) => {
    if (!d) return "";
    const date = d instanceof Date ? d : new Date(d);
    return date.toISOString().slice(0, 10);
  });

  // Collections
  eleventyConfig.addCollection("thesisChapters", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/thesis/*.md")
      .sort((a, b) => (a.data.order || 0) - (b.data.order || 0));
  });

  eleventyConfig.addCollection("projects", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/projects/*.md")
      .sort((a, b) => (a.data.order || 0) - (b.data.order || 0));
  });

  eleventyConfig.addCollection("ducks", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/ducks/*.md")
      .sort((a, b) => {
        // Newest first
        const da = new Date(a.data.date).getTime() || 0;
        const db = new Date(b.data.date).getTime() || 0;
        return db - da;
      });
  });

  // ---------------------------------------------------------------------
  // injectDucks: takes rendered chapter HTML, finds all ducks whose
  // anchor.chapter matches the given slug, locates each anchor phrase
  // and inserts a small inline duck right after the paragraph that
  // contains the phrase. Falls back to a console warning if the phrase
  // can't be located.
  // ---------------------------------------------------------------------
  function escapeAttr(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function fmtDate(d) {
    if (!d) return "";
    const dt = d instanceof Date ? d : new Date(d);
    if (isNaN(dt.getTime())) return String(d);
    return dt.toISOString().slice(0, 10);
  }

  const PATH_PREFIX = "/theyellowduckphenomenon";
  function withPrefix(u) {
    if (!u) return u;
    if (u.startsWith("http://") || u.startsWith("https://") || u.startsWith("#")) return u;
    if (u.startsWith(PATH_PREFIX)) return u;
    if (u.startsWith("/")) return PATH_PREFIX + u;
    return u;
  }

  eleventyConfig.addFilter("injectDucks", function(html, chapterSlug, allDucks, duckImg) {
    if (!html || !allDucks) return html;
    const ducks = allDucks.filter(d =>
      d.data.anchor && d.data.anchor.chapter === chapterSlug
    );
    if (!ducks.length) return html;

    let result = html;
    for (const d of ducks) {
      const phrase = d.data.anchor && d.data.anchor.after;
      if (!phrase) continue;

      const needle = phrase.slice(0, 60);
      const idx = result.indexOf(needle);
      if (idx === -1) {
        console.warn(`[ducks] anchor phrase not found in ${chapterSlug}: "${needle}"`);
        continue;
      }
      const endP = result.indexOf("</p>", idx);
      if (endP === -1) continue;
      const insertAt = endP + 4;

      const rawTarget = d.data.kind === "project" ? d.data.target : d.url;
      const target = withPrefix(rawTarget);
      const dateStr = fmtDate(d.data.date);
      const label = `${dateStr}  ·  ${d.data.title}`;
      const duckHtml =
        `<a class="branch-duck-link" href="${escapeAttr(target)}" ` +
        `data-kind="${escapeAttr(d.data.kind)}" ` +
        `data-date="${escapeAttr(dateStr)}" ` +
        `data-title="${escapeAttr(d.data.title)}">` +
        `<img class="duck branch-duck" src="${escapeAttr(duckImg)}" alt="" ` +
        `data-label="${escapeAttr(label)}"></a>`;

      result = result.slice(0, insertAt) + duckHtml + result.slice(insertAt);
    }
    return result;
  });

  return {
    pathPrefix: "/theyellowduckphenomenon/",
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};

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

  // Collections
  eleventyConfig.addCollection("thesisChapters", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/thesis/*.md")
      .sort((a, b) => (a.data.order || 0) - (b.data.order || 0));
  });

  eleventyConfig.addCollection("projects", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/projects/*.md")
      .sort((a, b) => (a.data.order || 0) - (b.data.order || 0));
  });

  return {
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

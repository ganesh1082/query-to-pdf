// A modern and clean Typst template for professional reports.

// Data import from the JSON file created by the Python script.
#let data = json("report_data.json")

// --- 1. CONFIGURATION ---

// Define a professional color palette.
#let colors = (
  primary: rgb("#1A2B42"),    // Deep navy blue for text and major headings.
  secondary: rgb("#4A5568"),  // Medium gray for subtitles and body text.
  accent: rgb("#D69E2E"),     // Golden-amber for accents, lines, and highlights.
  background: rgb("#F7FAFC"), // A very light gray for the page background.
  white: rgb("#FFFFFF"),
)

// Define a font scheme for a clean, modern look.
// Typst can automatically fetch Google Fonts.
// For custom fonts, place .ttf/.otf files in your project and use:
// body: font("fonts/MyCustomFont.ttf")
#let fonts = (
  body: "Helvetica",
  heading: "Helvetica",
)

// --- 2. DOCUMENT SETUP ---

// Set global document properties.
#set document(
  author: data.author,
  title: data.title,
)

// Configure the page layout and text defaults.
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, x: 2cm),
  fill: colors.background,
)
#set text(font: fonts.body, size: 10.5pt, fill: colors.secondary)

// --- 3. STYLING RULES ---

// Style for level-1 headings.
#show heading.where(level: 1): it => {
  v(1.5em, weak: true)
  align(left)[
    rect(width: 4cm, height: 1.5pt, fill: colors.accent)
    v(0.4em)
    text(size: 20pt, weight: "bold", fill: colors.primary)[#it]
  ]
  v(1em, weak: true)
}

// Justify paragraphs
#set par(justify: true)

// Style for hyperlinks.
#show link: set text(fill: colors.accent.darken(10%))

// --- 4. REUSABLE COMPONENTS ---

// Custom page header.
#let header(title) = align(right)[
  text(size: 9pt, weight: "medium", fill: colors.secondary)[#title.replace("_", " ")]
]

// Custom page footer with company name and page number.
#let footer(company) = {
  line(length: 100%, stroke: 0.5pt + colors.accent)
  v(0.5em)
  grid(
    columns: (auto, 1fr),
    text(size: 9pt, weight: "bold", fill: colors.primary)[#company],
    align(right, text(size: 9pt, fill: colors.secondary)[Page #context counter(page).display()])
  )
}

// Cover Page Layout.
#let cover-page(title, subtitle, author, company, date, logo_path) = {
  set page(header: none, footer: none, margin: (x: 0cm, y: 0cm))
  
  rect(width: 100%, height: 100%, fill: colors.background)
  place(left, rect(width: 6cm, height: 100%, fill: colors.primary))
  
  align(left + top, pad(left: 8cm, top: 4cm, right: 2cm)[
    if logo_path != none and logo_path != "" and logo_path != "none" and file.exists(logo_path) {
      image(logo_path, width: 4cm)
      v(2em)
    }
    
    text(font: fonts.heading, size: 32pt, weight: "bold", fill: colors.primary)[
      #title.replace("_", " ")
    ]
    v(1em)
    
    text(font: fonts.body, size: 16pt, fill: colors.secondary)[#subtitle]
    v(2fr)
    
    text(size: 11pt, fill: colors.primary)
    line(length: 100%, stroke: 0.5pt + colors.accent)
    v(1em)
    table(
      columns: (auto, auto),
      column-gutter: 2cm,
      align: left,
      [*Author:*], [#author],
      [*Organization:*], [#company],
      [*Date:*], [#date],
    )
  ])
  pagebreak()
}

// --- 5. DOCUMENT BODY ---

// Generate the Cover Page first (without header/footer).
#cover-page(
  data.title,
  data.subtitle,
  data.author,
  data.company,
  data.date,
  data.logo_path,
)

// Apply header and footer to all pages after the cover.
#set page(
  header: header(data.title),
  footer: footer(data.company)
)

// Generate the Table of Contents.
#outline(
  title: text(24pt, font: fonts.heading, weight: "bold", fill: colors.primary, "Contents"),
  depth: 1,
  indent: 2em
)
#pagebreak()

// Loop through sections and generate content pages.
#for section in data.sections {
  heading(section.title)
  
  raw(section.content)
  
  if "chart_path" in section and section.chart_path != none and section.chart_path != "" {
    v(1.5em)
    figure(
      align(center, image(section.chart_path, width: 85%)),
      caption: [
        #strong[Figure #context counter(figure).display():] #section.title
      ],
      kind: "chart",
      supplement: [Chart]
    )
    v(1em)
  }
  
  pagebreak()
}
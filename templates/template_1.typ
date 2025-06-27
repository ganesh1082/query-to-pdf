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
#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm), fill: colors.background)
#set text(font: fonts.body, size: 11pt, lang: "en", fill: colors.secondary)
#set par(leading: 0.65em, justify: true)

// --- 3. STYLING RULES ---

// Style for level-1 headings.
#show heading: it => {
  set text(font: fonts.heading, weight: "bold", fill: colors.primary)
  v(18pt, weak: true)
  it
  v(10pt, weak: true)
  line(length: 100%, stroke: 0.5pt + colors.accent)
  v(12pt, weak: true)
}
#set heading(numbering: "1.")

// Style for hyperlinks.
#show link: set text(fill: colors.accent.darken(10%))

// --- 4. PAGE HEADER AND FOOTER ---

#set page(
  header: align(right)[
    #text(9pt, fill: colors.secondary)[#data.company]
  ],
  footer: context align(center)[
    #text(9pt, fill: colors.secondary)[
      Page #context counter(page).display()
    ]
  ]
)

// --- 5. COVER PAGE FUNCTION ---

#let cover_page(title, subtitle, author, company, date, logo_path) = {
  align(center)[
    v(3cm, weak: true)
    
    // Display logo if available - separated from other elements
    if logo_path != none and logo_path != "" and logo_path != "none" {
      align(center)[
        [#image(logo_path, width: 3cm)]
      ]
      v(3cm, weak: true)
    }
    
    text(font: fonts.heading, weight: "bold", size: 28pt, fill: colors.primary)[#title.replace("_", " ")]
    v(0.5cm, weak: true)
    text(font: fonts.body, size: 16pt, fill: colors.secondary)[#subtitle]
    
    v(1fr)
  ]
    
  line(length: 100%, stroke: 1pt + colors.accent)
  v(0.5cm)
    
  grid(
    columns: (1fr, 1fr),
    gutter: 20pt,
    align: (left, left),
    text(11pt, [
      #strong[Author:] #author \
      #strong[Organization:] #company
    ]),
    text(11pt, [
      #strong[Publication Date:] #date
    ]),
  )
  pagebreak()
}

// --- 6. DOCUMENT BODY ---

// Generate cover page
#cover_page(
  data.title,
  data.subtitle,
  data.author,
  data.company,
  data.date,
  data.logo_path
)

// Table of contents
#outline(
  title: text(24pt,   colors.primary, "Table of Contents"),
  depth: 1,
  indent: 2em
)
#pagebreak()

// Generate sections from data
#for section in data.sections {
  heading(section.title)

  // Display the content as text
  text(section.content)
  
  if "chart_path" in section and section.chart_path != none and section.chart_path != "" {
    v(1em)
    figure(
      image(section.chart_path, width: 90%),
      caption: [Visualization for: #section.title]
    )
  }
  
  pagebreak()
}
// A modern 2-column Typst template for professional reports.

// Data import from the JSON file created by the Python script.
#let data = json("report_data.json")

// --- 1. CONFIGURATION ---

// Define a professional color palette with the specified colors.
#let colors = (
  primary: rgb("#AF3029"),    // Deep red for headings and accents.
  secondary: rgb("#25241C"),  // Dark charcoal for body text.
  accent: rgb("#AF3029"),     // Deep red for accents (same as primary).
  background: rgb("#FFFCF0"), // Warm off-white for page background.
  white: rgb("#FFFFFF"),
)

// Define a font scheme with IBM Plex Mono for titles and Trebuchet MS for body.
// Using system fonts with fallbacks for better availability
#let fonts = (
  body: ("Trebuchet MS", "Arial", "Helvetica", "sans-serif"),
  heading: ("IBM Plex Mono", "Courier New", "monospace"),
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
  line(length: 100%, stroke: 0.5pt + colors.primary)
  v(12pt, weak: true)
}
#set heading(numbering: "1.")

// Style for hyperlinks.
#show link: set text(fill: colors.primary.darken(10%))

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
    // Display logo if available - separated from other elements

    #image(logo_path, width: 3cm)
    
    
    #text(font: fonts.heading, weight: "bold", size: 28pt, fill: colors.primary)[#title.replace("_", " ")]

    #text(font: fonts.body, size: 16pt, fill: colors.secondary)[#subtitle]
    

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

// --- 6. TWO-COLUMN LAYOUT FUNCTION ---

#let two_column_section(title, content, chart_path, chart_type, is_last: false) = {
  heading(title)

  // Create a grid layout with two rows: first half for text, second half for visuals
  grid(
    rows: (1fr, 1fr),  // Split page into two equal halves
    gutter: 20pt,
    align: (left, left),
    
    // First half: Two-column text layout (top half of page)
    columns(2)[
      #raw(content)
    ],
    
    // Second half: Chart/visuals area (bottom half of page)
    if chart_path != "" and chart_path != none and chart_type != "none" {
      v(1em)
      figure(
        image(chart_path, width: 70%),
        caption: "Visualization for: " + title
      )

    } else if chart_type == "none" {
      // For sections intentionally without charts, leave the second half empty
      align(center)[
        // Empty space for sections that don't need charts
      ]
    } else {
      // If chart is missing due to error, show placeholder
      align(center)[
        text(fill: colors.secondary.lighten(30%), style: "italic")[
          Chart not available for: #title
        ]
      ]
    }
  )

  // Only add page break if this is not the last section
  if not is_last {
    pagebreak()
  }
}

// --- 7. DOCUMENT BODY ---

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
  title: text(24pt, colors.primary, "Table of Contents"),
  depth: 1,
  indent: 2em
)
#pagebreak()

// Generate sections from data with 2-column layout
#for (i, section) in data.sections.enumerate() {
  two_column_section(
    section.title,
    section.content,
    if "chart_path" in section {
      section.chart_path
    } else {
      ""
    },
    if "chart_type" in section {
      section.chart_type
    } else {
      ""
    },
    is_last: i == data.sections.len() - 1
  )
} 
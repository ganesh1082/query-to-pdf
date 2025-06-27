#let data = json("report_data.json")

// Custom color palette for Template A
#let primary = rgb(34, 87, 122)
#let accent = rgb(255, 193, 7)
#let bg = rgb(240, 248, 255)

// Document setup
#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm), fill: bg)
#set text(font: "Helvetica", size: 11pt, lang: "en")
#set par(leading: 0.65em, justify: true)

// Custom header and footer
#set page(
  header: align(left)[
    text(font: "Helvetica", weight: "bold", size: 12pt, fill: primary)[#data.company]
  ],
  footer: context align(right)[
    text(font: "Helvetica", size: 9pt, fill: accent)[Page #counter(page).display()]
  ]
)

// Cover page with accent bar and logo
#let cover-page(title, subtitle, author, company, date, logo-path) = show {
  rect(width: 100%, height: 0.7cm, fill: accent)
  align(center)[
    v(2.5cm, weak: true)
    if logo-path != none and logo-path != "" {
      image(logo-path, width: 3.5cm)
      v(1cm, weak: true)
    }
    text(font: "Helvetica", weight: "bold", size: 30pt, fill: primary)[#title.replace("_", " ")]
    v(0.5cm, weak: true)
    text(font: "Helvetica", size: 16pt, fill: primary)[#subtitle]
    v(1fr)
  ]
  line(length: 100%, stroke: 1.5pt + accent)
  v(0.5cm)
  grid(
    columns: (1fr, 1fr),
    gutter: 20pt,
    align: (left, left),
    text(12pt, [
      strong[Author:] #author \
      strong[Organization:] #company
    ]),
    text(12pt, [
      strong[Publication Date:] #date
    ]),
  )
  pagebreak()
}

// Table of contents with accent color
#outline(
  title: text(22pt, fill: accent, "Table of Contents"),
  depth: 1,
  indent: 2em
)
#pagebreak()

// Section rendering with sidebar
#for section in data.sections {
  rect(width: 0.4cm, height: 100%, fill: accent)
  heading(section.title)
  raw(section.content)
  if "chart_path" in section and section.chart_path != none and section.chart_path != "" {
    v(1em)
    figure(
      image(section.chart_path, width: 90%),
      caption: [Visualization for: #section.title]
    )
  }
  pagebreak()
} 
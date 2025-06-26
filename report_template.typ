// query_to_pdf/report_template.typ

#let data = json("report_data.json")

// Document setup
#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))
#set text(font: "Helvetica", size: 11pt, lang: "en")
#set par(leading: 0.65em, justify: true)

// Style headings
#show heading: it => {
  set text(font: "Helvetica", weight: "bold", fill: rgb(13, 32, 61))
  v(18pt, weak: true)
  it
  v(10pt, weak: true)
  line(length: 100%, stroke: 0.5pt + rgb(189, 195, 199))
  v(12pt, weak: true)
}
#set heading(numbering: "1.")

// Page header and footer
#set page(
  header: align(right)[
    #text(9pt, fill: rgb(85, 85, 85))[#data.company]
  ],
  footer: context align(center)[
    #text(9pt, fill: rgb(136, 136, 136))[
      Page #counter(page).display()
    ]
  ]
)

// Cover page function
#let cover-page(title, subtitle, author, company, date, logo-path) = {
  align(center)[
    v(3cm, weak: true)
    
    if logo-path != none and logo-path != "" {
      image(logo-path, width: 3cm)
      v(1.5cm, weak: true)
    }
    
    text(font: "Helvetica", weight: "bold", size: 28pt, fill: rgb(13, 32, 61))[#title.replace("_", " ")]
    v(0.5cm, weak: true)
    text(font: "Helvetica", size: 16pt, fill: rgb(45, 55, 72))[#subtitle]
    
    v(1fr)
  ]
    
  line(length: 100%, stroke: 1pt + rgb(74, 144, 226))
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

// === DOCUMENT START ===

// Generate cover page
#cover-page(
  data.title,
  data.subtitle,
  data.author,
  data.company,
  data.date,
  data.logo_path
)

// Table of contents
#outline(
  title: text(24pt, fill: rgb(13, 32, 61), "Table of Contents"),
  depth: 1,
  indent: 2em
)
#pagebreak()

// Generate sections from data
#for section in data.sections {
  heading(section.title)

  // The content is now pre-formatted, so we can use it directly.
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
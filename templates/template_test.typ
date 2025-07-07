// Simple test template to debug content rendering

#let data = json("report_data.json")

#set document(
  author: data.author,
  title: data.title,
)

#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))

#text(size: 24pt, weight: "bold")[Test Template - Content Debug]

#for (i, section) in data.sections.enumerate() {
  #text(size: 18pt, weight: "bold")[Section {i}: {section.title}]
  
  #text(size: 12pt)[Content length: {section.content.len()} characters]
  
  #text(size: 11pt)[{section.content}]
  
  #if "chart_path" in section and section.chart_path != "" {
    #text(size: 10pt, fill: red)[Chart path: {section.chart_path}]
  }
  
  #pagebreak()
} 
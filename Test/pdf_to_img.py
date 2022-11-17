import office

# pdf->png
name = office.pdf.pdf2imgs(
    pdf_path='./file/' + '湘环罚字【2014】2号.pdf',
    out_dir='file/'
)
print(name)
#!/usr/bin/python

from glob import glob

def word_freq(text):
    return text.count("the")

def word_count(current,new):
    return current+new

books = glob("books/*")
book_text = [open(book,"r").read() for book in books]

print reduce(word_count,map(word_freq,book_text))

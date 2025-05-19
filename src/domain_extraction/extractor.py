import spacy
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

nlp = spacy.load("en_core_web_sm")
doc = nlp("""
This is a sentence. It contains 3 components:
1) Technique
2) Skill
3) Luck
""")
print([(w.text, w.pos_) for w in doc])

md = (MarkdownIt('commonmark', {'breaks': True, 'html': True})
    .use(front_matter_plugin)
    .use(footnote_plugin)
    .enable('table'))

text = """
Section 1
------------
The patterns are:
- All caps
- Title case
- Numbered prefixes (e.g., 1., 1.1., CHAPTER X)

Section 2
-------------
Tools:
- OpenIE6 (https://github.com/allenai/openie6)
- ClausIE (rule-based, Java)
- MinIE (more compact facts)

List the names of the sections in the above piece of text. Be very brief.
"""

tokens = md.parse(text)
print(tokens)

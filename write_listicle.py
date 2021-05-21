import json
from collections import defaultdict

"""
year,title,author,genre,notes
"""

class Col(object):
    pass

class Year(Col):
    label = 'Year'
    def render(self, dat):
        pubdat = dat['publication date']
        if pubdat is None:
            return ''
        return str(pubdat)

class Title(Col):
    label = 'Title'
    def render(self, dat):
        title = dat['en_label']
        wtitle = dat['wiki_title']
        cite = ''
        for refid in TITLE_TO_REFS[title]:
            cite += f'<ref name="{refid}"/>'
        if title == wtitle:
            # Don't need to pipe
            link = f"''[[{title}]]''"
        else:
            link = f"''[[{wtitle}|{title}]]''"
        return link + cite

class Author(Col):
    # TODO: Probably should have grabbed disambiguated wiki title for author
    label = 'Author'
    def render(self, dat):
        auth = dat['author']
        # Special case: Sins of the Cities of the Plain
        if auth is None:
            return '"Jack Saul"'
        elif auth == 'Michael Nelson':
            # disambiguate
            return '[[Michael Nelson (novelist)|Michael Nelson]]'
        return f'[[{auth}]]'

GENRE_BLACKLIST = {
        'novel', 'LGBT literature', 'novella',
        None, # Comes up with some weird q-entities that don't have en labels
}
class Genre(Col):
    label = 'Genre'
    def render(self, dat):
        genre_strings = []
        for genre in dat['genre']:
            if genre in GENRE_BLACKLIST:
                continue
            genre_strings.append(genre)
        return ', '.join(genre_strings)

COUNTRY_TRANS = {
        'United States of America': 'USA',
        'United Kingdom': 'UK',
}
class Country(Col):
    label = 'Country'
    def render(self, dat):
        coo = dat['country of origin']
        return COUNTRY_TRANS.get(coo, coo) or ''

class Language(Col):
    label = 'Language'
    def render(self, dat):
        return dat['language'] or ''

class Notes(Col):
    label = 'Notes'
    def render(self, dat):
        return ''

COL_CLASSES = [Year, Title, Author,
        #Genre, 
        Country,
        #Language,
        Notes,
]

COLS = [cls() for cls in COL_CLASSES]

def render_header():
    col_labels = ' !! '.join([col.label for col in COLS])
    return '''{| class="wikitable sortable"
|-
! ''' + col_labels

def render_row(novel, note):
    rowa = ' || '.join([col.render(novel) for col in COLS[:-1]])
    return f'''|-
| {rowa}
| {note}'''

def render_table(noveldat):
    yield render_header()
    for novel in noveldat:
        pubdate = novel['publication date']
        # Pre-stonewall. Special case for Maurice, since written long before published.
        if pubdate is None or pubdate >= 1969 and novel['wiki_title'] != 'Maurice (novel)':
            continue
        if novel['en_label'] in TITLE_BLACKLIST:
            continue
        wtitle = novel['wiki_title']
        note = NOTES.get(wtitle, '')
        try:
            yield render_row(novel, note)
        except Exception as e:
            print("Error handling novel: " + novel['en_label'])
            raise e
    yield '|}'

TITLE_BLACKLIST = {
        'Fanny Hill',
        "A Year in Arcadia: Kyllenion",
        "Cecil Dreeme",
        "The Confusions of Young Törless",
        "Death in Rome",
        "The Talented Mr. Ripley",
        "Advise and Consent",
        "The Wanting Seed",
        "The Spanish Gardener",
        # Protagonist has homosexual experiences in school. Doesn't seem to be central concern.
        "Pied Piper of Lovers",
}

NOTES = {
    "Joseph and His Friend: A Story of Pennsylvania": "The title characters have a close, affectionate friendship, but are not physically intimate, and both have romantic relationships with women. Scholars disagree as to whether the story should be understood as having a gay subtext.",
    "The Sins of the Cities of the Plain": "A pornographic novel purporting to be the memoirs of a male prostitute.",
    "O Ateneu": "Depicts [[situational homosexuality]] among students in an all-male boarding school.",
    "The Picture of Dorian Gray": "The novel's allusions to homosexuality and homosexual desire were seen as scandalous when it was first published serially in [[Lippincott's Monthly Magazine]]. Wilde subsequently made several revisions to excise homoerotic themes before the work was published in book format. An unexpurgated version was published in 2011 which further included passages deleted by an editor at Lippincott's before initial publication.<ref>https://www.theguardian.com/books/2011/apr/27/dorian-gray-oscar-wilde-uncensored</ref>",
    "Teleny, or The Reverse of the Medal": "Pornographic novel published anonymously. Believed to be the work of multiple authors, possibly including [[Oscar Wilde]].",
    "Imre: A Memorandum": "Notable for being among the earliest sympathetic portrayals of homosexuality. The main characters, lovers Imre and Oswald, are happy and united at the end of the story. Only a small printing of 500 copies was issued in Italy (Stevenson was an American writing in Europe). Reissued in 2003.",
    "Death in Venice": "The main character, an aging writer, develops an infatuation with a beautiful adolescent boy. Subject of a number of adaptations, most notably a [[Death in Venice (film)|1971 film]] by [[Luchino Visconti]].",
    "The Charioteer": "Due to its positive portrayal of homosexuality, it was not able to be published in the US until 1959. Renault would continue to explore homosexual themes in her later novels - beginning with the 1956 ''The Last of the Wine'' - but using an Ancient Greek setting to evade censorship.",
    "The Last of the Wine": "The first of several historical novels that Renault would write which dealt with homosexuality in an Ancient Greek setting.",
    "City of Night": "Follows a [[Male prostitution|hustler]] in his travels across America. Includes discussion of the [[Cooper Do-nuts Riot]], an early event in the gay liberation movement, seen as a precursor to the [[Stonewall riots]].",
    "Tell Me How Long the Train's Been Gone": "A retrospective examination of the life and relationships of a bisexual black man from [[Harlem]].",
    "In Search of Lost Time": "Some critics surmise that the narrator is presented as a closeted homosexual. The first chapter of the fourth volume includes a detailed account of a sexual encounter between two men. Proust himself was gay, but not publicly.",
    "Quatrefoil: A Modern Novel": "Among the first novels to favourably portray homosexuality.",


}

BIC = {
        "The Sins of the Cities of the Plain",
        "Marius the Epicurean",
        "Memoirs of Arthur Hamilton",
        "The Deemster",
        "The Picture of Dorian Gray",
        "Tim",
        "Teleny, or The Reverse of the Medal",
        "The Green Carnation",
}

GLR = {
        'Maurice',
        "The City and the Pillar",
        "The Picture of Dorian Gray",
        "In Search of Lost Time",
        "Giovanni's Room",
        "The Charioteer",
        "A Single Man",
}

LOST = {
        "Other Voices, Other Rooms",
        "The City and the Pillar",
}

GLBT1 = {
        "Imre: A Memorandum",
}
GLBT2 = {
        "Bertram Cope's Year",
}
GLBT3 = {
        "Better Angel",
}

REFCOLLECTIONS = ([BIC, "BIC"], [GLR, "GLR"], [LOST, "Lost"],
    [GLBT1, "GLBTQ-Am-1"],
    [GLBT2, "GLBTQ-Am-2"],
    [GLBT3, "GLBTQ-Am-3"],
)

TITLE_TO_REFS = defaultdict(list)
for titles, refid in REFCOLLECTIONS:
    for title in titles:
        TITLE_TO_REFS[title].append(refid)

def main():
    dat_fname = 'noveldat.json'
    with open(dat_fname) as f:
        noveldat = json.load(f)

    out_fname = 'table.wiki'
    with open(out_fname, 'w') as f:
        for line in render_table(noveldat):
            f.write(line + '\n')

if __name__ == '__main__':
    main()

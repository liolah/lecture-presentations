"""Deck families: independent design systems that share this engine (tools/).

A family lives in families/<name>/ and owns its design/ (tokens, principles, patterns, decisions, template),
courses/ (content profiles) and lib/ (its pattern builders).

Project folders (fixed; see CLAUDE.md):
    modules/<Module name> - <code>/<Deck folder>/   deliverables + source/ (build scripts + tagged source deck)
    reference/                                      original inputs (REV1.0 decks, sheet PDFs, answer keys); read-only
    .build/                                         scratch only (renders, intermediate builds); git-ignored

Which family applies is resolved, in order, from:
    1. an explicit --family flag / argument
    2. the deck itself: custom document property `deck_family` (written by every family builder)
    3. the DECK_FAMILY environment variable (set by a family's build script before importing deckkit)
No default: guessing would let one family's rules leak into another's decks.
"""
import json, os, re, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMILIES = os.path.join(ROOT, 'families')
MODULES = os.path.join(ROOT, 'modules')
REFERENCE = os.path.join(ROOT, 'reference')
SCRATCH = os.path.join(ROOT, '.build')
PROP = 'deck_family'


def scratch(*parts):
    """A path under .build/ (created): the only place intermediate output may go."""
    p = os.path.join(SCRATCH, *parts)
    os.makedirs(p, exist_ok=True)
    return p


def names():
    return sorted(d for d in os.listdir(FAMILIES) if os.path.isfile(os.path.join(FAMILIES, d, 'FAMILY.md')))


def path(fam, *parts):
    return os.path.join(FAMILIES, fam, *parts)


def from_deck(deck):
    """Read the `deck_family` custom property from a .pptx (None if absent)."""
    try:
        z = zipfile.ZipFile(deck)
        if 'docProps/custom.xml' not in z.namelist():
            return None
        x = z.read('docProps/custom.xml').decode('utf-8', 'replace')
        m = re.search(r'name="%s"[^>]*>\s*<vt:lpwstr>([^<]+)</vt:lpwstr>' % PROP, x)
        return m.group(1) if m else None
    except (OSError, zipfile.BadZipFile):
        return None


def resolve(flag=None, deck=None):
    fam = flag or (from_deck(deck) if deck else None) or os.environ.get('DECK_FAMILY')
    if not fam:
        raise SystemExit(f'No deck family given. Use --family {{{"|".join(names())}}} '
                         f'(or set DECK_FAMILY); decks built by a family carry it automatically.')
    if fam not in names():
        raise SystemExit(f'Unknown deck family "{fam}". Known: {", ".join(names())}')
    return fam


def tokens(fam):
    # DECK_TOKENS: an explicit tokens file, used only by exploration variants (families/<f>/explore/...)
    p = os.environ.get('DECK_TOKENS') or path(fam, 'design', 'tokens.json')
    if not os.path.exists(p):
        raise SystemExit(f'Family "{fam}" has no design system yet ({p}). Run its discovery phase first '
                         f'(see families/{fam}/FAMILY.md).')
    return json.load(open(p, encoding='utf-8'))


def use(fam):
    """Call at the top of a family build script, BEFORE importing deckkit / family libs."""
    import sys
    os.environ['DECK_FAMILY'] = resolve(fam)
    lib = path(fam, 'lib')
    tools = os.path.join(ROOT, 'tools')
    for p in (tools, lib):
        if p not in sys.path:
            sys.path.insert(0, p)
    return fam

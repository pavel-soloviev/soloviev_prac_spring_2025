import locale
import gettext

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("WCount", "po", ["ru_RU.UTF-8"]),
    ("C", "UTF-8"): gettext.NullTranslations(),
}

def ngettext(text, textn, n):
    return LOCALES[locale.getlocale()].ngettext(text, textn, n)

#translation = gettext.translation("WCount", "po", fallback=True)
#_, ngettext = translation.gettext, translation.ngettext
while s := input():
    N = len(s.split())
    for loc in LOCALES:
        locale.setlocale(locale.LC_ALL, loc)
        print(ngettext("Entered {} word", "Entered {} words", N).format(N))


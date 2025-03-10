import cmd
from calendar import TextCalendar

DIGITS = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
          'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
TEENS = {'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
         'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19}
DECS = {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90}
ANY = DIGITS | TEENS | DECS


class My_calend(cmd.Cmd):
    prompt = "cmd>> "

    def do_prmonth(self, arg):
        """Print a month’s calendar as returned by formatmonth()."""
        year, mon = int(arg.split()[0]), int(arg.split()[1])
        TextCalendar.prmonth(TextCalendar(), year, mon)

    def do_pryear(self, arg):
        """Print the calendar for an entire year as returned by formatyear()."""
        year = int(arg)
        TextCalendar.pryear(TextCalendar(), year)

    def do_EOF(self, arg):
        return 1


if __name__ == '__main__':
    My_calend().cmdloop()


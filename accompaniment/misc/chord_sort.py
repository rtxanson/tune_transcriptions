import os, sys

_TUNE_DELIM = '***********************************************'

_OUTPUT_HEADING = """# Tunes by chord profile

Data Source: [Vashon Celtic Tunes](http://home.comcast.net/~saustin98/lark/)

Tunes included: ~550

Note: Some keys and tune types are left out, if there were not enough to sort
into a reasonable amount. Headings include amount of tunes read, but obviously,
not all these will be gruoped and displayed.

Chords are listed in order of frequency.

"""

class Tune(object):

    def __repr__(self):
        return "<Tune: %s, %d parts, %s, %s>" % ( self.title
                                                , len(self.parts.keys())
                                                , self.type
                                                , self.key
                                                )

    def parse_parts(self, parts):
        from collections import OrderedDict

        def do_it(p):
            measures = []
            for l in p:
                measures.extend(l.strip().split('|'))
            cleaned = []

            for m in measures:
                _m = m.strip()
                cleaned.append(_m.split())

            return cleaned

        parsed = OrderedDict()

        for k, v in parts.iteritems():
            parsed[k] = do_it(v)

        return parsed

    def split_parts(self, chunk):
        from collections import OrderedDict

        parts = OrderedDict()
        part_key = None

        for l in chunk:

            if 'Note' in l:
                continue

            if 'Part' in l:
                part_key = l.replace('Part', '').replace(':', '').strip()
                continue

            if part_key in parts:
                parts[part_key].append(l)
            else:
                parts[part_key] = [l]

        # TODO: parse parts into measures and chords.
        return self.parse_parts(parts)

    def process_type_sig(self, l):
        type, _, sig = l.partition(' in ')
        return type, sig

    def unique_the_chords(self, parts):
        # TODO: remove repeat symbol (:) and sort in order of descending
        # frequency.
        from collections import defaultdict
        from operator import itemgetter

        _all = defaultdict(int)
        for k, v in parts.iteritems():
            part_chords = list(sum(v, []))
            for p in part_chords:
                _all[p] += 1

        sorted_chords = sorted( list(_all.iteritems()), key=itemgetter(1), reverse=True)
        chords = [a[0] for a in sorted_chords]
        freqs = [a[1] for a in sorted_chords]

        return chords, freqs

    def chord_perc(self):
        _max = float(sum(self.chord_freq))
        perc = lambda x: str(int(round( (float(x)/_max)*100 ))) + '%'

        cs = ["%s (%s)" % (name, perc(c)) for name, c in zip(self.unique_chords, self.chord_freq)]
        return ', '.join(cs)

    def __init__(self, chunk):
        self.raw_chunk = [l for l in chunk if l != _TUNE_DELIM]

        self.title = self.raw_chunk[0]
        self.type, self.key = self.process_type_sig(self.raw_chunk[1])

        self.parts = self.split_parts(self.raw_chunk[2::])
        self.unique_chords, self.chord_freq = self.unique_the_chords(self.parts)
        self.title = self.title + ': ' + self.chord_perc()

def chunk_tunes(lines):
    chunks, chunk = [], []

    for l in lines:

        if l == _TUNE_DELIM:
            if len(chunk) > 0:
                chunks.append(chunk)
            chunk = []

        chunk.append(l)

    return chunks


def main():
    _f = sys.argv[1]

    with open(_f, 'r') as F:
        lines = [l.strip() for l in F.readlines()
                 if l.startswith('    ')
                ]

    print >> sys.stderr, 'lines: %d' % len(lines)
    tunes = map(Tune, chunk_tunes(lines))
    print >> sys.stderr, 'tunes: %d' % len(tunes)
    print >> sys.stdout, ''
    print >> sys.stdout, ''

    # TODO: grab all the keys, and sort by largest, then start to figure
    # out common progressions

    tunes_g = [t for t in tunes if t.key == 'D' and t.type == 'Reel']
    tune_types = list(set((t.type for t in tunes)))

    filtered_types = [
        'Jig',
        'Polka',
        'Barndance',
        'Reel',
        'Slip Jig',
    ]

    from collections import defaultdict

    keys_without_tunes = []

    for _type in filtered_types:
        print >> sys.stdout, "## " + _type
        print >> sys.stdout, ""

        _keys_for_tune_type = list(set((t.key for t in tunes if t.type == _type)))

        for tune_key in _keys_for_tune_type:

            tunes_in_key = [t for t in tunes if t.key == tune_key and t.type == _type]

            all_chords = defaultdict(list)
            for t in tunes_in_key:
                # TODO: order unique_chords by chord frequency in tune
                all_chords[ ', '.join(t.unique_chords) ].append(t.title)

            print_tunes = []
            for k, v in all_chords.iteritems():
                if len(v) > 1:
                    print_tunes.append('**%s**' % k)
                    print_tunes.append('')
                    for n in v:
                        print_tunes.append(' - ' + n)
                    print_tunes.append('')

            if len(print_tunes) > 0:
                print >> sys.stdout, "###", tune_key, "(%d tunes)" % len(tunes_in_key)
                print >> sys.stdout, ''
                print >> sys.stdout, '\n'.join(print_tunes)
                print >> sys.stdout, ''
            else:
                keys_without_tunes.append(
                    "%s %s (%d tunes)" % (_type, tune_key, len(tunes_in_key))
                )

    # print len(tunes_g)

    # first_a_parts = defaultdict(list)

    # for g in tunes_g:
    #     first_a_parts[ '|'.join([':'.join(b) for b in g.parts.get('A')]) ].append(g.title)

    # for k, v in first_a_parts.iteritems():
    #     if len(v) > 1:
    #         print k
    #         for n in v:
    #             print '  - ' + n

    # all_chords = defaultdict(list)

    # for g in tunes_g:
    #     all_chords[ '|'.join(g.unique_chords) ].append(g.title)

    # for k, v in all_chords.iteritems():
    #     if len(v) > 1:
    #         print k
    #         for n in v:
    #             print '  - ' + n


if __name__ == "__main__":
    sys.exit(main())

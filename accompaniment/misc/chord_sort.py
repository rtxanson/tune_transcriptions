import os, sys

_TUNE_DELIM = '***********************************************'

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

    def __init__(self, chunk):
        self.raw_chunk = [l for l in chunk if l != _TUNE_DELIM]

        self.title = self.raw_chunk[0]
        self.type, self.key = self.process_type_sig(self.raw_chunk[1])

        self.parts = self.split_parts(self.raw_chunk[2::])

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

    print 'lines: %d' % len(lines)
    tunes = map(Tune, chunk_tunes(lines))
    print 'tunes: %d' % len(tunes)
    print
    print

    # TODO: grab all the keys, and sort by largest, then start to figure
    # out common progressions

    tunes_g = [t for t in tunes if t.key == 'D' and t.type == 'Reel']

    print len(tunes_g)

    from collections import defaultdict

    first_a_parts = defaultdict(list)

    for g in tunes_g:
        first_a_parts[ '|'.join([':'.join(b) for b in g.parts.get('A')]) ].append(g.title)

    for k, v in first_a_parts.iteritems():
        if len(v) > 1:
            print k
            for n in v:
                print '  - ' + n



if __name__ == "__main__":
    sys.exit(main())

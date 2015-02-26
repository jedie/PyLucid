import re
from pprint import pprint


TYPE_SCRIPT="script"
TYPE_HTML="html"

SCRIPT_RE = re.compile(r'''
    (\<script.*?\>.*?\</script\>)
    |
    (\<noscript.*?\>.*?\</noscript\>)
''', re.VERBOSE | re.UNICODE | re.IGNORECASE | re.DOTALL)


def iter_html_and_script(html):
    data = SCRIPT_RE.split(html)
    for part in data:
        if part is None:
            continue
        part=part.strip()
        if not part:
            continue

        # print(part)
        # print("-------------------------------")

        if part.lower().endswith("</script>") or part.lower().endswith("</noscript>"):
            yield (TYPE_SCRIPT, part)
        else:
            yield (TYPE_HTML, part)


if __name__ == "__main__":
    html="""\
<h1>foo</h1><noscript>No <strong>Script!
iwehjfw</strong>
</noscript>
<script type="text/javascript">XXX
yyy</script><p>bar
wrewe
</p><script>
wdfvw
JavaScript here!</script>
<p>end</p>"""

    for kind, content in iter_html_and_script(html):
        print("%s: %r" % (kind, content))
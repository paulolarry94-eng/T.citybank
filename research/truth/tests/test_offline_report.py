"""Tests of research/portfolio/make_offline_report.py (the single-file copy of the portfolio report)."""
import os, sys, json, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "portfolio"))
import make_offline_report as R


class Offline(unittest.TestCase):
    def test_build_embeds_the_page_every_csv_and_d3_and_survives_script_tags(self):
        d = tempfile.mkdtemp()
        open(os.path.join(d, "index.html"), "w").write("<div id='x'>hello</div><script>var a = '</script>';</script>")
        open(os.path.join(d, "alpha.csv"), "w").write("a,b\n1,2\n")
        open(os.path.join(d, "beta.csv"), "w").write("c\n</script>\n")
        html = R.build(d, d3_js="/*d3 stub*/", built="2030-01-01")
        self.assertIn("/*d3 stub*/", html); self.assertIn("Permission to use, copy, modify", html)
        self.assertIn('<div id="dash-root">', html)
        self.assertIn('"alpha": "a,b\\n1,2\\n"', html); self.assertIn('"beta"', html)
        self.assertIn("2030-01-01", html)
        self.assertEqual(html.count("</script>"), 3)                               # d3, runtime, injection: embedded text never closes a script
        self.assertNotIn("<!--", html.split("</head>")[1])                         # and never opens a comment in the body part

    def test_wrong_d3_build_is_refused(self):
        p = os.path.join(tempfile.mkdtemp(), "d3.min.js")
        open(p, "w").write("not d3")
        with self.assertRaises(SystemExit):
            R.get_d3(p)

    def test_the_committed_offline_copy_matches_the_page_and_data(self):
        d = R.REPORT
        out = os.path.join(d, "report_offline.html")
        if not os.path.exists(out):
            self.skipTest("report_offline.html not built")
        html = open(out, encoding="utf-8").read()
        page = open(os.path.join(d, "index.html"), encoding="utf-8").read()
        self.assertIn(json.dumps(page).replace("</", "<\\/"), html)                    # the page as it is now
        for f in os.listdir(d):
            if f.endswith(".csv"):
                self.assertIn(json.dumps(open(os.path.join(d, f), encoding="utf-8").read())[1:60].replace("</", "<\\/"), html, f)


if __name__ == "__main__":
    unittest.main()

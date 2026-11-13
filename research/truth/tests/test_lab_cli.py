"""Tests of tools/lab.py (the front door for testing a new strategy):  python3 -m unittest discover -s research/truth/tests -v
The tests write only into temporary folders and never touch the real strategies folder or the real memory."""
import os, sys, json, shutil, subprocess, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(HERE, ".."))
import lab as L
import memory as MEMORY
import protocol as P

_TMP_MEM = tempfile.mkdtemp()
MEMORY.MEM = _TMP_MEM; MEMORY.LEDGER = os.path.join(_TMP_MEM, "ledger.jsonl")


class Scaffold(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.kw = dict(strat_dir=self.d, ledger_names=set(), today="2030-01-02")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def make(self, name="zz_unit_idea_v1", **over):
        a = dict(name=name, family=["reversal", "Intraday"], markets=["EURUSD", "XAUUSD"], timeframes=["H1"], hypothesis="Index funds must rebalance; they pay.")
        a.update(over)
        return L.scaffold(a["name"], a["family"], a["markets"], a["timeframes"], a["hypothesis"], **self.kw)

    def test_file_is_created_filled_in_and_loads_like_the_lab_loads_it(self):
        p = self.make()
        txt = open(p).read()
        self.assertIn("PRE-REGISTRATION", txt); self.assertIn("2030-01-02", txt)
        r = L.check_strategy(p)
        self.assertEqual(r["errors"], [])
        i = r["info"]
        self.assertEqual(i["name"], "zz_unit_idea_v1"); self.assertEqual(i["markets"], ["EURUSD", "XAUUSD"]); self.assertEqual(i["timeframes"], ["H1"])
        self.assertEqual(i["family"], ["reversal", "intraday"])                   # tags are lower-cased so the priors match
        mg = 1
        for v in P.DEFAULT_MGMT.values():
            mg *= len(v)
        self.assertEqual(i["settings_per_market"], 2 * mg)                         # template grid {"n": [20, 55]} x 1 timeframe x the lab's default management grid
        self.assertEqual(i["settings_per_market"], 24)
        self.assertEqual(len(i["fingerprint"]), 64)

    def test_unfilled_hypothesis_is_an_error_until_written(self):
        p = self.make("zz_unit_idea_v2", hypothesis="")
        self.assertTrue(any("HYPOTHESIS" in e for e in L.check_strategy(p)["errors"]))

    def test_template_name_default_is_an_error(self):
        p = os.path.join(self.d, "placeholder.py")
        shutil.copy(L.TEMPLATE, p)
        r = L.check_strategy(p)
        self.assertTrue(any("NAME" in e for e in r["errors"]))

    def test_bad_names_and_empty_inputs_are_refused(self):
        for bad in ("Bad", "9lives", "a", "has space", "UPPER_v1", "x" * 61, "a-b-c"):
            with self.assertRaises(L.LabError, msg=bad):
                self.make(bad)
        with self.assertRaises(L.LabError):
            self.make(family=[])
        with self.assertRaises(L.LabError):
            self.make(markets=[])
        with self.assertRaises(L.LabError):
            self.make(name="template")                                              # would collide with TEMPLATE.py on case-insensitive disks

    def test_names_are_never_reused_and_the_hint_bumps_the_version(self):
        self.make("zz_unit_idea_v1")
        with self.assertRaises(L.LabError) as c:                                    # an existing file
            self.make("zz_unit_idea_v1")
        self.assertIn("zz_unit_idea_v2", str(c.exception))
        with self.assertRaises(L.LabError):                                         # a name only in the ledger (file deleted or run elsewhere)
            L.scaffold("tested_before", ["trend"], ["EURUSD"], ["H1"], "x", strat_dir=self.d, ledger_names={"tested_before"})
        self.assertEqual(L.bump("tokyo_fix"), "tokyo_fix_v2"); self.assertEqual(L.bump("a_v9"), "a_v10")

    def test_markets_without_costs_or_data_are_refused(self):
        with self.assertRaises(L.LabError) as c:
            self.make(markets=["EURUSD", "NOPE"])
        self.assertIn("NOPE", str(c.exception))
        p = self.make("zz_unit_idea_v3")
        text = open(p).read().replace('"EURUSD", "XAUUSD"', '"EURUSD", "NOPE2"')   # edited later: the check must catch it
        open(p, "w").write(text)
        self.assertTrue(any("NOPE2" in e for e in L.check_strategy(p)["errors"]))

    def test_large_grids_are_flagged(self):
        p = self.make("zz_unit_idea_v4")
        text = open(p).read().replace('GRID = {"n": [20, 55]}', 'GRID = {"n": list(range(1, 60)), "k": [1, 2, 3]}')
        open(p, "w").write(text)
        r = L.check_strategy(p)
        self.assertEqual(r["errors"], [])
        self.assertTrue(any("lottery" in w for w in r["warnings"]))

    def test_broken_file_raises_a_clear_error(self):
        p = os.path.join(self.d, "broken.py")
        open(p, "w").write("NAME = 'x'\nthis is not python\n")
        with self.assertRaises(L.LabError):
            L.check_strategy(p)
        q = os.path.join(self.d, "lacks.py")
        open(q, "w").write("NAME = 'x'\n")
        with self.assertRaises(L.LabError) as c:
            L.check_strategy(q)
        self.assertIn("lacks", str(c.exception))


class Commit(unittest.TestCase):
    def test_is_committed_tracks_the_pre_registration(self):
        d = tempfile.mkdtemp()
        try:
            run = lambda *a: subprocess.run(["git", "-C", d, *a], capture_output=True, check=True)
            run("init", "-q"); run("config", "user.email", "t@example.invalid"); run("config", "user.name", "t")
            f = os.path.join(d, "s.py")
            open(f, "w").write("x = 1\n")
            self.assertFalse(L.is_committed(f, d))                                  # untracked
            run("add", "s.py"); self.assertFalse(L.is_committed(f, d))              # staged, not committed
            run("commit", "-q", "-m", "one"); self.assertTrue(L.is_committed(f, d))
            open(f, "a").write("x = 2\n"); self.assertFalse(L.is_committed(f, d))   # edited after the commit
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Memory(unittest.TestCase):
    def test_priors_text_reports_counts_and_the_all_rejected_warning(self):
        for i, v in enumerate(("Rejected: a", "Rejected: b", "Rejected: c")):
            MEMORY.record(dict(name=f"zz_prior_{i}", date="2030-01-0%d" % (i + 1), family=["zz_tag"], verdict=v, configs=3, fingerprint=f"f{i}"))
        t = L.priors_text(["zz_tag"])
        self.assertIn("3 tested, 0 survived", t); self.assertIn("All rejected", t)
        MEMORY.record(dict(name="zz_prior_ok", date="2030-02-01", family=["zz_tag"], verdict="Tier B: forward-test candidate", configs=3, fingerprint="f9"))
        self.assertIn("4 tested, 1 survived", L.priors_text(["zz_tag"]))
        self.assertNotIn("All rejected", L.priors_text(["zz_tag"]))
        self.assertIn("No earlier idea", L.priors_text(["zz_nothing_like_this"]))

    def test_configuration_counts_use_one_key_name(self):
        self.assertEqual(MEMORY.n_configs(dict(configs=5)), 5); self.assertEqual(MEMORY.n_configs(dict(configurations=7)), 7)
        self.assertEqual(MEMORY.n_configs(dict(name="x")), 0)
        MEMORY.record(dict(name="zz_cfg_old_key", date="2030-04-01", family=["zz_cfg"], verdict="Rejected: x", configurations=11, fingerprint="g1"))
        e = [r for r in MEMORY.load() if r["name"] == "zz_cfg_old_key"][0]
        self.assertEqual(e["configs"], 11); self.assertNotIn("configurations", e)


class Catalogue(unittest.TestCase):
    def test_catalogue_lists_every_idea_once_in_the_right_group_and_escapes_pipes(self):
        rows = [dict(name="zz_cat_a", date="2030-03-01", family=["x"], verdict="Tier B: forward-test candidate", configs=5),
                dict(name="zz_cat_b|pipe", date="2030-03-02", family=["x", "y"], verdict="Rejected: no configuration passed", configs=7, evidence="research/results/zz"),
                dict(name="zz_cat_c", date="2030-03-03", family=[], verdict="Report of the mix (no new selection)", configs=1),
                dict(name="zz_cat_d", date="2030-03-04", family=["y"], verdict="FAILS (pre-registered look)", configs=2)]
        txt = L.catalogue_text(rows, MEMORY)
        self.assertIn("4 ideas, about 15 configurations: 1 survivors or candidates, 2 rejected, 1 other", txt)
        for r in rows:
            self.assertEqual(txt.count(r["name"].replace("|", "\\|")), 1)
        sec = {k: txt.split("## " + k)[1].split("\n## ")[0] for k in ("Survivors and candidates", "Rejected", "Other")}
        self.assertIn("zz_cat_a", sec["Survivors and candidates"]); self.assertIn("zz_cat_d", sec["Rejected"]); self.assertIn("zz_cat_c", sec["Other"])
        self.assertEqual(txt, L.catalogue_text(list(reversed(rows)), MEMORY))        # deterministic whatever the ledger order


if __name__ == "__main__":
    unittest.main()

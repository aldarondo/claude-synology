"""
Unit tests for pure logic functions — no network, no NAS required.

Run: python -m pytest tests/test_unit.py -v
     python tests/test_unit.py          (unittest runner)
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.edit_env import parse_env, update_env
from skills.deploy import https_to_ssh
from skills.ssh_shell import looks_destructive
from lib.ssh import _clean


# ── edit_env ─────────────────────────────────────────────────────────────────

class TestParseEnv(unittest.TestCase):

    def test_simple_key_value(self):
        lines = parse_env("FOO=bar\nBAZ=qux\n")
        keys = [k for k, _ in lines if k]
        self.assertEqual(keys, ["FOO", "BAZ"])

    def test_preserves_comments(self):
        text = "# comment\nFOO=bar\n"
        lines = parse_env(text)
        self.assertIsNone(lines[0][0])   # comment → no key
        self.assertEqual(lines[1][0], "FOO")

    def test_preserves_blank_lines(self):
        lines = parse_env("\nFOO=bar\n\n")
        self.assertIsNone(lines[0][0])  # blank
        self.assertEqual(lines[1][0], "FOO")
        self.assertIsNone(lines[2][0])  # blank

    def test_value_with_equals(self):
        lines = parse_env("URL=http://host:8080/path?a=1\n")
        key, line = lines[0]
        self.assertEqual(key, "URL")
        self.assertIn("http://host:8080/path?a=1", line)

    def test_empty_value(self):
        lines = parse_env("TOKEN=\n")
        self.assertEqual(lines[0][0], "TOKEN")


class TestUpdateEnv(unittest.TestCase):

    def test_update_existing_key(self):
        result = update_env("FOO=old\n", {"FOO": "new"})
        self.assertIn("FOO=new", result)
        self.assertNotIn("FOO=old", result)

    def test_append_new_key(self):
        result = update_env("FOO=bar\n", {"NEW_KEY": "value"})
        self.assertIn("FOO=bar", result)
        self.assertIn("NEW_KEY=value", result)

    def test_preserves_comments(self):
        result = update_env("# comment\nFOO=bar\n", {"FOO": "new"})
        self.assertIn("# comment", result)
        self.assertIn("FOO=new", result)

    def test_multiple_updates(self):
        result = update_env("A=1\nB=2\n", {"A": "10", "B": "20"})
        self.assertIn("A=10", result)
        self.assertIn("B=20", result)

    def test_update_and_append(self):
        result = update_env("A=1\n", {"A": "99", "NEW": "hello"})
        self.assertIn("A=99", result)
        self.assertIn("NEW=hello", result)

    def test_empty_file(self):
        result = update_env("", {"TOKEN": "abc"})
        self.assertIn("TOKEN=abc", result)

    def test_ends_with_newline(self):
        result = update_env("FOO=bar\n", {"FOO": "new"})
        self.assertTrue(result.endswith("\n"))

    def test_blank_line_separator_before_appended_keys(self):
        result = update_env("FOO=bar\n", {"NEW": "value"})
        lines = result.splitlines()
        # Should have a blank line separating existing content from new keys
        self.assertIn("", lines)


# ── deploy.py ────────────────────────────────────────────────────────────────

class TestHttpsToSsh(unittest.TestCase):

    def test_converts_github_https_to_ssh(self):
        url = "https://github.com/aldarondo/brian-mcp.git"
        self.assertEqual(https_to_ssh(url), "git@github.com:aldarondo/brian-mcp.git")

    def test_passthrough_ssh_url(self):
        url = "git@github.com:aldarondo/brian-mcp.git"
        self.assertEqual(https_to_ssh(url), url)

    def test_passthrough_non_github_url(self):
        url = "https://gitlab.com/user/repo.git"
        self.assertEqual(https_to_ssh(url), url)

    def test_no_git_extension(self):
        url = "https://github.com/aldarondo/brian-mcp"
        self.assertEqual(https_to_ssh(url), "git@github.com:aldarondo/brian-mcp")


# ── ssh_shell.py ─────────────────────────────────────────────────────────────

class TestLooksDestructive(unittest.TestCase):

    def test_rm_is_destructive(self):
        self.assertTrue(looks_destructive("rm -rf /tmp/test"))

    def test_shutdown_is_destructive(self):
        self.assertTrue(looks_destructive("shutdown now"))

    def test_ls_is_safe(self):
        self.assertFalse(looks_destructive("ls /volume1/docker"))

    def test_docker_ps_is_safe(self):
        self.assertFalse(looks_destructive("docker ps"))

    def test_reboot_is_destructive(self):
        self.assertTrue(looks_destructive("reboot"))

    def test_redirect_to_root_is_destructive(self):
        self.assertTrue(looks_destructive("echo bad > /etc/passwd"))


# ── lib/ssh.py _clean ────────────────────────────────────────────────────────

class TestClean(unittest.TestCase):

    def test_strips_ansi_colors(self):
        text = "\x1b[32mGreen text\x1b[0m"
        self.assertEqual(_clean(text), "Green text")

    def test_strips_cursor_hide_show(self):
        text = "\x1b[?25lhidden\x1b[?25h"
        self.assertEqual(_clean(text), "hidden")

    def test_strips_carriage_returns(self):
        text = "line1\r\nline2\r\n"
        self.assertNotIn("\r", _clean(text))

    def test_strips_non_ascii(self):
        # Docker compose spinner characters (Braille)
        text = "Running \u2819 container"
        result = _clean(text)
        self.assertNotIn("\u2819", result)
        self.assertIn("Running", result)

    def test_strips_shell_prompt(self):
        text = "some output\ncharles@supergirl:~$ "
        result = _clean(text)
        self.assertNotIn("$", result)
        self.assertIn("some output", result)

    def test_clean_output_unchanged(self):
        text = "NAME\tSTATUS\nollama\tUp 9 days"
        self.assertEqual(_clean(text), text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

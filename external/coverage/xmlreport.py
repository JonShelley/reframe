# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""XML reporting for coverage.py"""

import os
import os.path
import sys
import time
import xml.dom.minidom

from coverage import __url__, __version__, files
from coverage.misc import isolate_module, human_sorted, human_sorted_items
from coverage.report import get_analysis_to_report

os = isolate_module(os)


DTD_URL = 'https://raw.githubusercontent.com/cobertura/web/master/htdocs/xml/coverage-04.dtd'


def rate(hit, num):
    """Return the fraction of `hit`/`num`, as a string."""
    if num == 0:
        return "1"
    else:
        return "%.4g" % (float(hit) / num)


class XmlReporter:
    """A reporter for writing Cobertura-style XML coverage results."""

    report_type = "XML report"

    def __init__(self, coverage):
        self.coverage = coverage
        self.config = self.coverage.config

        self.source_paths = set()
        if self.config.source:
            for src in self.config.source:
                if os.path.exists(src):
                    if not self.config.relative_files:
                        src = files.canonical_filename(src)
                    self.source_paths.add(src)
        self.packages = {}
        self.xml_out = None

    def report(self, morfs, outfile=None):
        """Generate a Cobertura-compatible XML report for `morfs`.

        `morfs` is a list of modules or file names.

        `outfile` is a file object to write the XML to.

        """
        # Initial setup.
        outfile = outfile or sys.stdout
        has_arcs = self.coverage.get_data().has_arcs()

        # Create the DOM that will store the data.
        impl = xml.dom.minidom.getDOMImplementation()
        self.xml_out = impl.createDocument(None, "coverage", None)

        # Write header stuff.
        xcoverage = self.xml_out.documentElement
        xcoverage.setAttribute("version", __version__)
        xcoverage.setAttribute("timestamp", str(int(time.time()*1000)))
        xcoverage.appendChild(self.xml_out.createComment(
            f" Generated by coverage.py: {__url__} "
            ))
        xcoverage.appendChild(self.xml_out.createComment(f" Based on {DTD_URL} "))

        # Call xml_file for each file in the data.
        for fr, analysis in get_analysis_to_report(self.coverage, morfs):
            self.xml_file(fr, analysis, has_arcs)

        xsources = self.xml_out.createElement("sources")
        xcoverage.appendChild(xsources)

        # Populate the XML DOM with the source info.
        for path in human_sorted(self.source_paths):
            xsource = self.xml_out.createElement("source")
            xsources.appendChild(xsource)
            txt = self.xml_out.createTextNode(path)
            xsource.appendChild(txt)

        lnum_tot, lhits_tot = 0, 0
        bnum_tot, bhits_tot = 0, 0

        xpackages = self.xml_out.createElement("packages")
        xcoverage.appendChild(xpackages)

        # Populate the XML DOM with the package info.
        for pkg_name, pkg_data in human_sorted_items(self.packages.items()):
            class_elts, lhits, lnum, bhits, bnum = pkg_data
            xpackage = self.xml_out.createElement("package")
            xpackages.appendChild(xpackage)
            xclasses = self.xml_out.createElement("classes")
            xpackage.appendChild(xclasses)
            for _, class_elt in human_sorted_items(class_elts.items()):
                xclasses.appendChild(class_elt)
            xpackage.setAttribute("name", pkg_name.replace(os.sep, '.'))
            xpackage.setAttribute("line-rate", rate(lhits, lnum))
            if has_arcs:
                branch_rate = rate(bhits, bnum)
            else:
                branch_rate = "0"
            xpackage.setAttribute("branch-rate", branch_rate)
            xpackage.setAttribute("complexity", "0")

            lnum_tot += lnum
            lhits_tot += lhits
            bnum_tot += bnum
            bhits_tot += bhits

        xcoverage.setAttribute("lines-valid", str(lnum_tot))
        xcoverage.setAttribute("lines-covered", str(lhits_tot))
        xcoverage.setAttribute("line-rate", rate(lhits_tot, lnum_tot))
        if has_arcs:
            xcoverage.setAttribute("branches-valid", str(bnum_tot))
            xcoverage.setAttribute("branches-covered", str(bhits_tot))
            xcoverage.setAttribute("branch-rate", rate(bhits_tot, bnum_tot))
        else:
            xcoverage.setAttribute("branches-covered", "0")
            xcoverage.setAttribute("branches-valid", "0")
            xcoverage.setAttribute("branch-rate", "0")
        xcoverage.setAttribute("complexity", "0")

        # Write the output file.
        outfile.write(serialize_xml(self.xml_out))

        # Return the total percentage.
        denom = lnum_tot + bnum_tot
        if denom == 0:
            pct = 0.0
        else:
            pct = 100.0 * (lhits_tot + bhits_tot) / denom
        return pct

    def xml_file(self, fr, analysis, has_arcs):
        """Add to the XML report for a single file."""

        if self.config.skip_empty:
            if analysis.numbers.n_statements == 0:
                return

        # Create the 'lines' and 'package' XML elements, which
        # are populated later.  Note that a package == a directory.
        filename = fr.filename.replace("\\", "/")
        for source_path in self.source_paths:
            source_path = files.canonical_filename(source_path)
            if filename.startswith(source_path.replace("\\", "/") + "/"):
                rel_name = filename[len(source_path)+1:]
                break
        else:
            rel_name = fr.relative_filename()
            self.source_paths.add(fr.filename[:-len(rel_name)].rstrip(r"\/"))

        dirname = os.path.dirname(rel_name) or "."
        dirname = "/".join(dirname.split("/")[:self.config.xml_package_depth])
        package_name = dirname.replace("/", ".")

        package = self.packages.setdefault(package_name, [{}, 0, 0, 0, 0])

        xclass = self.xml_out.createElement("class")

        xclass.appendChild(self.xml_out.createElement("methods"))

        xlines = self.xml_out.createElement("lines")
        xclass.appendChild(xlines)

        xclass.setAttribute("name", os.path.relpath(rel_name, dirname))
        xclass.setAttribute("filename", rel_name.replace("\\", "/"))
        xclass.setAttribute("complexity", "0")

        branch_stats = analysis.branch_stats()
        missing_branch_arcs = analysis.missing_branch_arcs()

        # For each statement, create an XML 'line' element.
        for line in sorted(analysis.statements):
            xline = self.xml_out.createElement("line")
            xline.setAttribute("number", str(line))

            # Q: can we get info about the number of times a statement is
            # executed?  If so, that should be recorded here.
            xline.setAttribute("hits", str(int(line not in analysis.missing)))

            if has_arcs:
                if line in branch_stats:
                    total, taken = branch_stats[line]
                    xline.setAttribute("branch", "true")
                    xline.setAttribute(
                        "condition-coverage",
                        "%d%% (%d/%d)" % (100*taken//total, taken, total)
                        )
                if line in missing_branch_arcs:
                    annlines = ["exit" if b < 0 else str(b) for b in missing_branch_arcs[line]]
                    xline.setAttribute("missing-branches", ",".join(annlines))
            xlines.appendChild(xline)

        class_lines = len(analysis.statements)
        class_hits = class_lines - len(analysis.missing)

        if has_arcs:
            class_branches = sum(t for t, k in branch_stats.values())
            missing_branches = sum(t - k for t, k in branch_stats.values())
            class_br_hits = class_branches - missing_branches
        else:
            class_branches = 0.0
            class_br_hits = 0.0

        # Finalize the statistics that are collected in the XML DOM.
        xclass.setAttribute("line-rate", rate(class_hits, class_lines))
        if has_arcs:
            branch_rate = rate(class_br_hits, class_branches)
        else:
            branch_rate = "0"
        xclass.setAttribute("branch-rate", branch_rate)

        package[0][rel_name] = xclass
        package[1] += class_hits
        package[2] += class_lines
        package[3] += class_br_hits
        package[4] += class_branches


def serialize_xml(dom):
    """Serialize a minidom node to XML."""
    return dom.toprettyxml()

# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Json reporting for coverage.py"""
import datetime
import json
import sys

from coverage import __version__
from coverage.report import get_analysis_to_report
from coverage.results import Numbers


class JsonReporter:
    """A reporter for writing JSON coverage results."""

    report_type = "JSON report"

    def __init__(self, coverage):
        self.coverage = coverage
        self.config = self.coverage.config
        self.total = Numbers(self.config.precision)
        self.report_data = {}

    def report(self, morfs, outfile=None):
        """Generate a json report for `morfs`.

        `morfs` is a list of modules or file names.

        `outfile` is a file object to write the json to

        """
        outfile = outfile or sys.stdout
        coverage_data = self.coverage.get_data()
        coverage_data.set_query_contexts(self.config.report_contexts)
        self.report_data["meta"] = {
            "version": __version__,
            "timestamp": datetime.datetime.now().isoformat(),
            "branch_coverage": coverage_data.has_arcs(),
            "show_contexts": self.config.json_show_contexts,
        }

        measured_files = {}
        for file_reporter, analysis in get_analysis_to_report(self.coverage, morfs):
            measured_files[file_reporter.relative_filename()] = self.report_one_file(
                coverage_data,
                analysis
            )

        self.report_data["files"] = measured_files

        self.report_data["totals"] = {
            'covered_lines': self.total.n_executed,
            'num_statements': self.total.n_statements,
            'percent_covered': self.total.pc_covered,
            'percent_covered_display': self.total.pc_covered_str,
            'missing_lines': self.total.n_missing,
            'excluded_lines': self.total.n_excluded,
        }

        if coverage_data.has_arcs():
            self.report_data["totals"].update({
                'num_branches': self.total.n_branches,
                'num_partial_branches': self.total.n_partial_branches,
                'covered_branches': self.total.n_executed_branches,
                'missing_branches': self.total.n_missing_branches,
            })

        json.dump(
            self.report_data,
            outfile,
            indent=4 if self.config.json_pretty_print else None
        )

        return self.total.n_statements and self.total.pc_covered

    def report_one_file(self, coverage_data, analysis):
        """Extract the relevant report data for a single file"""
        nums = analysis.numbers
        self.total += nums
        summary = {
            'covered_lines': nums.n_executed,
            'num_statements': nums.n_statements,
            'percent_covered': nums.pc_covered,
            'percent_covered_display': nums.pc_covered_str,
            'missing_lines': nums.n_missing,
            'excluded_lines': nums.n_excluded,
        }
        reported_file = {
            'executed_lines': sorted(analysis.executed),
            'summary': summary,
            'missing_lines': sorted(analysis.missing),
            'excluded_lines': sorted(analysis.excluded),
        }
        if self.config.json_show_contexts:
            reported_file['contexts'] = analysis.data.contexts_by_lineno(analysis.filename)
        if coverage_data.has_arcs():
            reported_file['summary'].update({
                'num_branches': nums.n_branches,
                'num_partial_branches': nums.n_partial_branches,
                'covered_branches': nums.n_executed_branches,
                'missing_branches': nums.n_missing_branches,
            })
        return reported_file

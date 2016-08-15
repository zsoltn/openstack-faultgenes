import csv
from launchpadlib.launchpad import Launchpad
from pprint import pprint


class Report(object):
    default_filepath = 'reports/bugdump.csv'
    default_project = 'openstack'
    default_importance = [
        'Critical'
    ]
    default_status = [
        'New', 'Incomplete', 'In Progress', 'Confirmed', 'Triaged',
        'Fix Committed'
    ]

    def __init__(self, debug=False, limit=None):
        self.limit = limit # Stop after 'limit' bugs if not None
        self.debug = debug
        self.dialect = csv.excel
        self.report = []
        if self.debug:
            print("Enabling debug output")
        if self.limit:
            print("Limiting report to %d bugs" % self.limit)

    def get_meta_keys(self):
        # Unused, but this is the list of all fields present in a 'task'.
        # A 'task' contain meta-data encapsulating a bug.
        return [
            'http_etag',
            'is_complete',
            'milestone_link',
            'resource_type_link',
            'bug_watch_link',
            'date_assigned',
            'date_closed',
            'date_confirmed',
            'date_fix_committed',
            'date_fix_released',
            'date_in_progress',
            'date_incomplete',
            'date_left_closed',
            'date_left_new',
            'date_triaged',
            'assignee_link',
            'bug_link',
            'bug_target_display_name',
            'bug_target_name',
            'date_created',
            'importance',
            'owner_link',
            'related_tasks_collection_link',
            'self_link',
            'status',
            'target_link',
            'title',
            'web_link'
        ]

    def get_ordered_fieldnames(self):
        return [
            'req',
            'bug',
            'version',
            'project',
            'component',
            'fault_class',
            'fault_type',
            'fault_description',
            'fault_symptom',
            'severity',
            'priority',
            'status',
            'mitigation',
            'log',
            'repro',
            'submitter',
            'assignee',
            'created',
            'deployment'
        ]

    def xstr(self, string):
        if string is None:
            return ''
        else:
            return string.encode('utf8')

    def create(self, project, importance, status):
        iteration = 0
        self.report = []
        lp = Launchpad.login_anonymously('just testing', 'production',
                                         'cache', version='devel')
        p = lp.projects[project]
        # pass status to filter on a subset of bugs
        bug_tasks = p.searchTasks(importance=importance, status=status)
        print("Found %d bugs in the %s project with importance %s" %
              (len(bug_tasks), project, str(importance)))
        for task in bug_tasks:
            if self.limit:
                self.limit -= 1
            bug = lp.bugs.getBugData(bug_id=task.bug.id)[0]
            if self.debug:
                print "Processing %s" % task
            else:
                iteration += 1
                (q, r) = divmod(iteration, 10)
                print '%s' % iteration if r == 0 else '.',
            # remap fields from lb task and bug
            empty = ''
            row = {
                'req':                  self.xstr(bug['bug_summary']),
                'bug':                  self.xstr(task.web_link),
                'version':              empty,
                'project':              self.xstr(task.bug_target_name),
                'component':            empty,
                'fault_class':          empty,
                'fault_type':           empty,
                'fault_description':    self.xstr(bug['description']),
                'fault_symptom':        empty,
                'severity':             self.xstr(task.importance),
                'priority':             empty,
                'status':               self.xstr(task.status),
                'mitigation':           empty,
                'log':                  empty,
                'repro':                empty,
                'submitter':            self.xstr(task.owner_link),
                'assignee':             self.xstr(task.assignee_link),
                'created':              self.xstr(str(task.date_created)),
                'deployment':           empty
            }
            self.report.append(row)
            if self.limit == 0:
                break
        print("\nFinished compiling table for project %s" % project)

    def dump(self):
        for row in self.report:
            pprint(row)

    def save(self, filepath):
        with open(filepath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile,
                                    fieldnames=self.get_ordered_fieldnames(),
                                    dialect=self.dialect)
            writer.writeheader()
            for row in self.report:
                try:
                    writer.writerow(row)
                except Exception as err:
                    print 'Row:'
                    pprint(row)
                    print 'Exception: %s' % err

        csvfile.close()

    def open(self, filepath):
        self.report = []
        with open(filepath, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, dialect=self.dialect)
            for row in reader:
                self.report.append(row)
        csvfile.close()


def generate_report(filepath=Report.default_filepath,
                    project=Report.default_project,
                    importance=Report.default_importance,
                    status=Report.default_status):
    report = Report(debug=False, limit=None)
    report.create(project, importance, status)
    report.save(filepath)

def read_report(filepath):
    report = Report(debug=False, limit=None)
    report.open(filepath)
    report.dump()

if __name__ == "__main__":
    generate_report(importance=['High'])
